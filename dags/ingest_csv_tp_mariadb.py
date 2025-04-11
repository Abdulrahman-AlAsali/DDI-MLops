from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from datetime import datetime

import sys
sys.path.append("/opt/airflow/scripts")
import data_ingest  

with DAG(
    dag_id='csv_to_mariadb',
    schedule_interval=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["csv", "mariadb", "ingestion"]
) as dag:

    ingest_task = PythonOperator(
        task_id='ingest_all_csvs',
        python_callable=data_ingest.ingest
    )

    trigger_transform = TriggerDagRunOperator(
        task_id="trigger_transform",
        trigger_dag_id="transform_matrix_tables",  # DAG ID of the transformation DAG
        # conf={"key": "value"},  # Optional configuration to pass to the triggered DAG
    )

    ingest_task >> trigger_transform
