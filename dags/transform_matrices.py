import pandas as pd
from sqlalchemy import create_engine, inspect
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dagrun_operator import TriggerDagRunOperator
from datetime import datetime

import sys
sys.path.append("/opt/airflow/scripts")
import data_transformation


with DAG(
    dag_id="transform_matrix_tables",
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
) as dag:

    transform_task = PythonOperator(
        task_id="transform_all_matrix_tables",
        python_callable=data_transformation.transform
    )

    trigger_model_dag = TriggerDagRunOperator(
        task_id="trigger_model_dag",
        trigger_dag_id="train_ddi_model",  # DAG ID of the model training DAG
    )

    transform_task >> trigger_model_dag
