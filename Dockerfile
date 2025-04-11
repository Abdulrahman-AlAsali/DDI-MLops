# Dockerfile
FROM apache/airflow:2.8.1-python3.10

USER root

# Install MariaDB client so Airflow can connect
RUN apt-get update && \
    apt-get install -y mariadb-client && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

USER airflow

# Copy DAGs and other files
COPY ./dags /opt/airflow/dags
COPY ./plugins /opt/airflow/plugins
COPY requirements.txt /opt/airflow/
COPY ./ddi /opt/airflow/ddi
COPY ./scripts /opt/airflow/scripts

RUN pip install --no-cache-dir -r /opt/airflow/requirements.txt
