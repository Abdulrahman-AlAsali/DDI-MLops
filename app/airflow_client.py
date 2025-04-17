"""
TODO:
Add logging
Timeouts and error catch
"""

from flask import jsonify, request
import requests

# Airflow connection details
AIRFLOW_URL = "http://airflow:8080/api/v1"  # assuming Airflow is running on the same container and is accessible
AIRFLOW_USERNAME = "admin"  # Airflow username (for basic authentication)
AIRFLOW_PASSWORD = "admin"  # Airflow password (for basic authentication)

def trigger_dag(dag_id: str):
    """Function to trigger a DAG run using Airflow's REST API."""
    url = f"{AIRFLOW_URL}/dags/{dag_id}/dagRuns"
    response = requests.post(
        url,
        json={}, 
        headers={"Content-Type": "application/json"},
        auth=(AIRFLOW_USERNAME, AIRFLOW_PASSWORD)
    )
    return response

def trigger_ingestion():
    """Trigger the CSV ingestion DAG."""
    response = trigger_dag('csv_to_mariadb')  # Trigger the DAG responsible for ingestion
    if response.status_code == 200:
        return jsonify({"message": "Ingestion DAG triggered successfully!"}), 200
    else:
        return jsonify({"message": "Failed to trigger Ingestion DAG", "error": response.text}), 500

def trigger_transformation():
    """Trigger the transformation DAG."""
    response = trigger_dag('transform_matrix_tables')  # Trigger the transformation DAG
    if response.status_code == 200:
        return jsonify({"message": "Transformation DAG triggered successfully!"}), 200
    else:
        return jsonify({"message": "Failed to trigger Transformation DAG", "error": response.text}), 500

def trigger_training():
    """Trigger the model training DAG."""
    response = trigger_dag('train_ddi_model')  # Trigger the model training DAG
    if response.status_code == 200:
        return jsonify({"message": "Training DAG triggered successfully!"}), 200
    else:
        return jsonify({"message": "Failed to trigger Training DAG", "error": response.text}), 500

def unpause_all_dags():
    """Unpause all DAGs using the Airflow REST API."""
    dags = ["csv_to_mariadb", "transform_matrix_tables", "train_ddi_model"]
    failed = []

    for dag in dags:
        patch_url = f"{AIRFLOW_URL}/dags/{dag}"
        patch_response = requests.patch(
            patch_url,
            json={"is_paused": False},
            headers={"Content-Type": "application/json"},
            auth=(AIRFLOW_USERNAME, AIRFLOW_PASSWORD)
        )
        if patch_response.status_code != 200:
            failed.append(dag)

    if not failed:
        return jsonify({"message": "All DAGs unpaused successfully!"}), 200
    else:
        return jsonify({
            "message": "Some DAGs failed to unpause",
            "failed_dags": failed
        }), 207

def pause_all_dags():
    """Unpause all DAGs using the Airflow REST API."""
    dags = ["csv_to_mariadb", "transform_matrix_tables", "train_ddi_model"]
    failed = []

    for dag in dags:
        patch_url = f"{AIRFLOW_URL}/dags/{dag}"
        patch_response = requests.patch(
            patch_url,
            json={"is_paused": True},
            headers={"Content-Type": "application/json"},
            auth=(AIRFLOW_USERNAME, AIRFLOW_PASSWORD)
        )
        if patch_response.status_code != 200:
            failed.append(dag)

    if not failed:
        return jsonify({"message": "All DAGs unpaused successfully!"}), 200
    else:
        return jsonify({
            "message": "Some DAGs failed to unpause",
            "failed_dags": failed
        }), 207
    
def is_dags_unpaused():
    """Check if all DAGs are unpaused using the Airflow REST API."""
    dags = ["csv_to_mariadb", "transform_matrix_tables", "train_ddi_model"]
    paused_dags = []

    for dag in dags:
        dag_url = f"{AIRFLOW_URL}/dags/{dag}"
        dag_response = requests.get(
            dag_url,
            headers={"Content-Type": "application/json"},
            auth=(AIRFLOW_USERNAME, AIRFLOW_PASSWORD)
        )
        if dag_response.status_code == 200:
            dag_info = dag_response.json()
            if dag_info.get("is_paused"):
                paused_dags.append(dag)

    return len(paused_dags) == 0