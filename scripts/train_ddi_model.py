import pandas as pd
# import numpy as np
import mlflow
from mlflow.models.signature import infer_signature
import mlflow.sklearn
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sqlalchemy import create_engine
import time

DB_URI = "mysql+pymysql://airflow:airflow@mariadb:3306/airflow"
DDI_TABLES = {
    'feat_sim_196', 'fingerprint_sim_196', 'MACCS_196', 'RWsim_196', 'smiles_sim_196', 'top196drugs', 'truelabel_196'
}


def load_data():
    engine = create_engine(DB_URI)
    
    labels_df = pd.read_sql("SELECT * FROM truelabel_196_transformed", con=engine)

    # Load transformed feature tables
    feature_tables = [table + "_transformed" for table in DDI_TABLES if not table in ["truelabel_196", "top196drugs"]]

    # Merge them one by one on drug IDs
    merged = labels_df.copy()
    for table in feature_tables:
        df = pd.read_sql_table(table, con=engine)
        df = df.rename(columns={"interaction_value": f"{table}_score"})
        merged = pd.merge(merged, df, on=["first_drug_id", "second_drug_id"], how="left")
    
    # Drop rows with missing values
    merged.dropna(inplace=True)
    
    return merged

def train():
    mlflow.set_experiment("ddi_prediction")

    with mlflow.start_run() as run:
        df = load_data()
        df.info()  # debugging
        X = df.drop(columns=["interaction_value", "first_drug_id", "second_drug_id"])
        y = df["interaction_value"]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        params = {
            "n_estimators": [50, 100],
            "max_depth": [5, 10, None]
        }
        
        # params = {
        #     "n_estimators": [50, 100, 200, 300],
        #     "max_depth": [5, 10, 20, None],
        #     "min_samples_split": [2, 5, 10],
        #     "min_samples_leaf": [1, 2, 4]
        # }

        model = RandomForestClassifier(random_state=42)
        grid = GridSearchCV(model, param_grid=params, scoring="accuracy", cv=3)

        start = time.time()
        grid.fit(X_train, y_train)
        end = time.time()


        best_model = grid.best_estimator_
        acc = best_model.score(X_test, y_test)

        # Get feature importances
        feature_importance = best_model.feature_importances_
        feature_names = X.columns
        importance_dict = dict(zip(feature_names, feature_importance))
        
        signature = infer_signature(X_test, best_model.predict(X_test))

        # Log everything to MLflow
        mlflow.set_tag("stage", "training")
        mlflow.set_tag("model_type", "RandomForest")
        mlflow.log_params(grid.best_params_)
        mlflow.log_metric("accuracy", acc)
        cv_results = grid.cv_results_
        for i, (params, acc) in enumerate(zip(cv_results["params"], cv_results["mean_test_score"])):
            mlflow.log_metric("cv_accuracy", acc, step=i)
            mlflow.log_dict(params, f"params_step_{i}.json")  # Logs each param set as a separate artifact

        mlflow.log_metric("training_time_sec", end - start)
        mlflow.log_metric("train_size", len(X_train))
        mlflow.log_metric("test_size", len(X_test))
        mlflow.log_metric("cv_mean_accuracy", grid.cv_results_["mean_test_score"].max())
        mlflow.log_metric("cv_std_accuracy", grid.cv_results_["std_test_score"][grid.best_index_])
        mlflow.log_dict(importance_dict, "feature_importance.json")

        mlflow.sklearn.log_model(best_model, "model", signature=signature, input_example=X_test.head())
        mlflow.register_model(
            model_uri=f"runs:/{run.info.run_id}/model",
            name="Drug-Interaction-Model"
        )

        return run.info.run_id



if __name__ == "__main__":
    train()