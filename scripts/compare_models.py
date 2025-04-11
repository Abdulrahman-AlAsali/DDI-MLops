from mlflow.tracking import MlflowClient

def compare(**kwargs):
    client = MlflowClient()
    model_name = "Drug-Interaction-Model"

    prod_versions = client.get_latest_versions(model_name, stages=["Production"])
    if not prod_versions:
        return True  # No production model exists yet

    prod_version = prod_versions[0]
    prod_score = client.get_run(prod_version.run_id).data.metrics.get("mse", float("inf"))

    candidate_run_id = kwargs["ti"].xcom_pull(task_ids="train_model", key="return_value")
    candidate_score = client.get_run(candidate_run_id).data.metrics.get("mse", float("inf"))

    return candidate_score < prod_score