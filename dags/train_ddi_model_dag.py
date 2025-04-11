from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

import sys
sys.path.append("/opt/airflow/scripts")
import train_ddi_model, compare_models, promote_model

with DAG(
    dag_id="train_ddi_model",
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False
) as dag:

    train_model = PythonOperator(
        task_id="train_model",
        python_callable=train_ddi_model.train,
        do_xcom_push=True
    )

    compare = PythonOperator(
        task_id="compare_models",
        python_callable=compare_models.compare,
        provide_context=True
    )

    promote = PythonOperator(
        task_id="promote_model",
        python_callable=promote_model.promote,
        provide_context=True
    )

    train_model >> compare >> promote
