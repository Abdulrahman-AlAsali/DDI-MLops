# 📥 Data Ingestion

This document outlines the data ingestion stage of the DDI-MLops pipeline, explaining what it is, why it’s important, and how it was implemented within the project.


## The What

### What is Data Ingestion?

Data ingestion is the process of collecting, importing, and loading raw data from various sources into a system where it can be stored and processed. In the context of the DDI-MLops pipeline, this stage is responsible for bringing in Drug-Drug Interaction (DDI) datasets that are later transformed and used to train the machine learning model.

### Key Components and Concepts
- **Apache Airflow**: Orchestrates and schedules the ingestion tasks.
- **Python Scripts**: Handle the actual extraction and loading of data.
- **MariaDB**: Serves as the data storage for the dataset.


### Input Dependencies
- **Source Data**: The ingestion process requires the datasets containing information about drug pairs and their interactions.
- **Location**:  the datasets should be in the `ddi` directory.
- **Data Format**: The input data must be in CSV format with a matrix structure and they be named `feat_sim_196.csv`, `fingerprint_sim_196.csv`, `MACCS_196.csv`, `RWsim_196.csv`, `smiles_sim_196.csv`, `top196drugs.csv`, and `truelabel_196.csv`. This structure is essential to support for transformation.

### Data Flow:
1. The data is placed by Docker in `opt/airflow/`.
2. Airflow triggers a DAG task that reads the CSV file using a Python operator.
3. The script parses and loads the data into the MariaDB database.

### Expected Output
- **Tables in MariaDB**: The raw CSV data is stored within MariaDB.

## The Why

### Why is this Stage Important?
- **Foundation of the Pipeline**: No pipeline can function without data. The ingestion phase is the first and most critical step to enable the flow of data throughout the system.
- **Consistency & Automation**: Ingesting data through scheduled, reproducible workflows ensures consistency, traceability, and operational efficiency.

### Why the Chosen Components Matter
- **Airflow**: Handles scheduling and retries, which is crucial for reliable data ingestion.
- **MariaDB**: A lightweight SQL database that supports structured data storage and easy integration with transformation tools.

# The How

## Implementation Steps
1.    **Airflow DAG**: A directed acyclic graph (DAG) is defined to schedule and control the ingestion process.
2.    **Custom Python Operator**: Reads the dataset and inserts it into the MariaDB table.

## Review of the Python Operator:

### The script firstly connects to MariaDB
``` python
def ingest():
    engine = create_engine(DB_URI)
```

### Then, finds all the CSVs in the the folder

``` python
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".csv"):
```

### Finally, reads the tables and stores the the read data in the database
``` python
            table_name = filename.replace(".csv", "")
            file_path = os.path.join(DATA_DIR, filename)
            df = pd.read_csv(file_path)
            df.to_sql(name=table_name, con=engine, if_exists='replace', index=False)
```


## Output Verification
- Using a client like HeidiSQL you can verify that the ingestion correctly ran.

# Related Page
- [Data ingestion](data_ingestion.md)
- [Data transformation](data_transformation.md)
- [Model training](model_training.md)
- [Caching](caching.md)
- [Application interface](application_interface.md)

# [GO to main page](../README.md)