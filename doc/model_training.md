# 🏋️‍♂️ Model Training

This document explains the model training stage of the DDI-MLops pipeline, describing what is done, why it's important, and how it was implemented.

## The What

### What is Model Training?

Model training is the stage where a machine learning algorithm learns patterns from historical data to make future predictions. In the DDI-MLops pipeline, a Random Forest Classifier is trained to predict drug-drug interactions based on the features from the transformation stage.


### Key Components and Concepts
- **Apache Airflow**: Schedules the model training task after the transformation tasks.
- **Scikit-learn**: Handles machine learning modeling, including training, evaluation, and prediction.
- **MLflow**: Experiment tracking, model logging, and model registry.
- **MariaDB**: Serves as the data storage for the dataset used in the training.


### Input Dependencies
- **Transformed Dataset**: Located in MariaDB.

- **Structured Format**: The input data must have no missing values, and must include:
    - `first_drug_id`
    - `second_drug_id`
    - `interaction_value`


### Data Loading Flow:
1. Training task is triggered via Airflow.
2. Data Loading Flow.
3. Merge features into a single DataFrame.
4. Train the model with using the DataFrame.

### Expected Output
- A trained Random Forest Classifier
- MLflow artifacts including:
    - Best hyperparameters
    - Accuracy metrics
    - Feature importance values
- Registered model in the MLflow Model Registry under the name `Drug-Interaction-Model`.

## The Why

### Why is this Stage Important?
- **Core Prediction Capability**: Without a trained model, the system cannot predict drug interactions.
- **Performance Optimisation**: Hyperparameter tuning improves model accuracy, reliability, and generalisation.
- **Experiment Reproducibility**: Tracking runs with MLflow ensures that experiments are versioned and auditable.


### Why the Chosen Components Matter
- **Scikit-learn**: Provides tools for model building, evaluation, and machine learning workflows.
- **MLflow**: Centralises experiment tracking, artifact storage, and model management.
- **Airflow**: Manages when and how the training script run, ensuring automation.
- **MariaDB**: Centralised data storage to simplify querying of data.

# The How

## Implementation Steps
1. Load data from the MariaDB
2. Formate the data is a way suitable for the training.
3. Trainin the AI model
4. Get statistics about the model performance
5. Save the resulting statistics and the model in MLflow  

## Review of the Code:

### The function is defined to load the true labels and the feature tables and merge them together
``` python
def load_data():
    labels_df = pd.read_sql("SELECT * FROM truelabel_196_transformed", con=engine)
    feature_tables = [table + "_transformed" for table in DDI_TABLES if not table in ["truelabel_196", "top196drugs"]]

    merged = labels_df.copy()
    for table in feature_tables:
        df = pd.read_sql_table(table, con=engine)
        df = df.rename(columns={"interaction_value": f"{table}_score"})
        merged = pd.merge(merged, df, on=["first_drug_id", "second_drug_id"], how="left")
```

### The training function saves an experiment on MLflow for the training and loads the data using the previously defined function
``` python
def train():
    mlflow.set_experiment("ddi_prediction")

    with mlflow.start_run() as run:
        df = load_data()
```

### the data is split into the input interaction `X` and the truth label `y` and a training:test split of 80:20 is set
``` python
        X = df.drop(columns=["interaction_value", "first_drug_id", "second_drug_id"])
        y = df["interaction_value"]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
```

### The training is done with the a Random Forest Classifier model and the best model is selected
``` python
        params = {
            "n_estimators": [50, 100],
            "max_depth": [5, 10, None]
        }

        model = RandomForestClassifier(random_state=42)
        grid = GridSearchCV(model, param_grid=params, scoring="accuracy", cv=3)

        grid.fit(X_train, y_train)

        best_model = grid.best_estimator_
```

### During the training the time to training is calculated and the feature importances is formated 
``` python
        start = time.time()
        grid.fit(X_train, y_train)
        end = time.time()

        feature_importance = best_model.feature_importances_
        feature_names = X.columns
        importance_dict = dict(zip(feature_names, feature_importance))
```
### The model and statistics are stored in MLflow
``` python
        mlflow.set_tag("stage", "training")
        mlflow.set_tag("model_type", "RandomForest")
        mlflow.log_params(grid.best_params_)
        mlflow.log_metric("accuracy", acc)
        cv_results = grid.cv_results_
        for i, (params, acc) in enumerate(zip(cv_results["params"], cv_results["mean_test_score"])):
            mlflow.log_metric("cv_accuracy", acc, step=i)
            mlflow.log_dict(params, f"params_step_{i}.json")  

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
```
## Output Verification
- MLflow UI (at port:`5000`) shows experiment runs, artifacts, and registered models.

# Related Page
- [Data ingestion](data_ingestion.md)
- [Data transformation](data_transformation.md)
- [Model training](model_training.md)
- [Caching](caching.md)
- [Application interface](application_interface.md)

# [GO to main page](../README.md)