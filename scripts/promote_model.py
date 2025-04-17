from mlflow.tracking import MlflowClient

def promote(**kwargs):
    passed = kwargs["ti"].xcom_pull(task_ids="compare_models")
    if not passed:
        print("Model did not outperform production. No promotion.")
        return

    client = MlflowClient()
    model_name = "Drug-Interaction-Model"
    new_version = client.get_latest_versions(model_name, stages=["None"])[0]

    client.transition_model_version_stage(
        name=model_name,
        version=new_version.version,
        stage="Staging"
    )

    client.transition_model_version_stage(
        name=model_name,
        version=new_version.version,
        stage="Production"
    )

    print(f"Model v{new_version.version} promoted to Production.")