import os
import pandas as pd
from sqlalchemy import create_engine

DATA_DIR = "/opt/airflow/ddi"

# MariaDB connection settings
DB_USER = "airflow"
DB_PASSWORD = "airflow"
DB_HOST = "mariadb"
DB_PORT = "3306"
DB_NAME = "airflow"

# SQLAlchemy connection string
DB_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def ingest():
    count = 0
    engine = create_engine(DB_URI)
    print(f"found {len(os.listdir(DATA_DIR))} files in {DATA_DIR}")
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".csv"):
            print(f"Processing file: {filename}")
            table_name = filename.replace(".csv", "")
            file_path = os.path.join(DATA_DIR, filename)
            df = pd.read_csv(file_path)
            df.to_sql(name=table_name, con=engine, if_exists='replace', index=False)
            print(f"Ingested {filename} into table `{table_name}`")
            count += 1
    print(f"Total files processed: {count}")