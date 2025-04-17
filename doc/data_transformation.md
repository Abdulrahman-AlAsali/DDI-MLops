# 🔄 Data Transformation

This document explains the data transformation stage in the DDI-MLops pipeline, detailing what it entails, its importance, and how it was executed within the project.

## The What

### What is Data Transformation?

Data transformation is the process of cleaning, converting, and engineering features from raw ingested data into a form that is usable by machine learning models. In this stage, the DDI dataset stored in MariaDB is preprocessed to ensure quality, consistency, and relevance.

### Key Components and Concepts
- **Apache Airflow**: Schedules the data transformation task after the ingestion tasks.
- **Pandas Python**: Handles data cleaning and the actual transformation of the data. 
- **MariaDB**: Serves as the data storage for the dataset.


### Input Dependencies
- **Tables from Ingestion Stage**: Tables stored in MariaDB.

### Data Flow:
1. Transformation task is triggered via Airflow.
2. A Python script queries MariaDB for the raw data.
3. Data is loaded into a Pandas DataFrame for transformation.
4. Data is saved back into new tables in MariaDB.

### Expected Output
- **Interaction Tables in MariaDB**: New tables in MariaDB formated with the following columns `first_drug_id`, `second_drug_id`, and `interaction_value`.

## The Why

### Why is this Stage Important?
- **Data Quality**: Raw data often contains noise, missing values, and inconsistencies. Transformation ensures high-quality inputs for training.

### Why the Chosen Components Matter
- **Pandas**: Provides efficient tools for cleaning and transforming data.
- **Airflow**: Manages when and how transformation scripts run, ensuring automation.
- **MariaDB**: Centralised data storage to simplify querying of data.

# The How

## Implementation Steps
1. Extract raw data from the MariaDB
2. Correct any mistakes from ingestion in the tables.
3. Transform the tables to the correct format
4. Remove duplicates
5. Save the transformed tables in MariaDB

## Review of the Python Operator:

### The script finds the loads the tables into a Pandas frame
``` python
def transform():
    all_tables = inspector.get_table_names()

    for table in all_tables:
        if not table in DDI_TABLES:
            continue
        
        df = pd.read_sql_table(table, con=engine)
```

### If the table is the drug names table make drug_name the column name and add an id

``` python
    if table == "top196drugs":
        original_col_name = df.columns[0]
        df.columns = ['drug_name']
        df.loc[-1] = [original_col_name]
        df.index = df.index + 1  
        df = df.sort_index()  
        df.reset_index(drop=True, inplace=True)
        df.insert(0, 'drug_id', range(1, len(df) + 1))
```

### Transform the matrix interaction tables into a sturctured table
``` python
            else:
                df.index = range(1, len(df) + 1) 
                df.columns = range(1, len(df.columns) + 1)

                df = df.stack().reset_index()
                df.columns = ['first_drug_id', 'second_drug_id', 'interaction_value']
```

### Remove any duplicates in the table
``` python
            df = df[df['first_drug_id'] <= df['second_drug_id']]
```

### Finally save the tables back into MariaDB
``` python
        new_table_name = f"{table}_transformed"
        df.to_sql(name=new_table_name, con=engine, if_exists='replace', index=False)
```

## Output Verification
- Check for the presence of the transformed tables in the MariaDB

# Related Page
- [Data ingestion](data_ingestion.md)
- [Data transformation](data_transformation.md)
- [Model training](model_training.md)
- [Caching](caching.md)
- [Application interface](application_interface.md)

# [GO to main page](../README.md)