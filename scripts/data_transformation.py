import pandas as pd
from sqlalchemy import create_engine, inspect

DB_URI = "mysql+pymysql://airflow:airflow@mariadb:3306/airflow"
DDI_TABLES = {
    'feat_sim_196', 'fingerprint_sim_196', 'MACCS_196', 'RWsim_196', 'smiles_sim_196', 'top196drugs', 'truelabel_196'
}

def transform():
    engine = create_engine(DB_URI)
    inspector = inspect(engine)
    all_tables = inspector.get_table_names()

    for table in all_tables:
        if not table in DDI_TABLES:
            continue  # Skip this one
        
        print(f"Transforming table: {table}")
        df = pd.read_sql_table(table, con=engine)

        if table == "top196drugs":
            original_col_name = df.columns[0]
            df.columns = ['drug_name']
            df.loc[-1] = [original_col_name]
            df.index = df.index + 1  
            df = df.sort_index()  
            df.reset_index(drop=True, inplace=True)
            df.insert(0, 'drug_id', range(1, len(df) + 1))
        else:
            # Convert DataFrame index and columns to numeric drug IDs
            df.index = range(1, len(df) + 1)  # Drug IDs (1-based)
            df.columns = range(1, len(df.columns) + 1)

            # Unpivot the matrix
            df = df.stack().reset_index()
            df.columns = ['first_drug_id', 'second_drug_id', 'interaction_value']

            # Drop symmetric duplicates or self-interactions
            df = df[df['first_drug_id'] <= df['second_drug_id']]

        # Save to new table
        new_table_name = f"{table}_transformed"
        df.to_sql(name=new_table_name, con=engine, if_exists='replace', index=False)
        print(f"Saved transformed table: {new_table_name}")
