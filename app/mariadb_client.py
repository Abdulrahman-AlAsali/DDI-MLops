import os
import redis
import pickle
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# SQLAlchemy connection URL
DATABASE_URL = 'mysql+pymysql://airflow:airflow@mariadb:3306/airflow'

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a configured "Session" class
Session = sessionmaker(bind=engine)

redis_client = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://redis:6379/0"), decode_responses=False)

def cache_result(key, data, ttl=3600):
    """Cache non-empty, non-null data in Redis."""
    if data is None:
        return

    if isinstance(data, dict):
        # Only cache if all values are not None
        if all(v is not None for v in data.values()):
            redis_client.setex(key, ttl, pickle.dumps(data))
    elif isinstance(data, list):
        # Only cache if list is not empty and has no None values
        if data and all(v is not None for v in data):
            redis_client.setex(key, ttl, pickle.dumps(data))
    else:
        # For single values (e.g., int, str)
        if data:
            redis_client.setex(key, ttl, pickle.dumps(data))

def get_all_drug_names():
    """Fetch all drug names from top196drugs table using SQLAlchemy."""

    cache_key = "drug_names"
    cached = redis_client.get(cache_key)
    if cached:
        return pickle.loads(cached)
    
    try:
        session = Session()
        # Use raw SQL if you don't have a mapped ORM class
        results = session.execute(text("SELECT drug_name FROM top196drugs_transformed")).fetchall()
        drug_names = [row[0] for row in results]
        cache_result(cache_key, drug_names)
        return drug_names
    except Exception as e:
        print(f"Error querying MariaDB via SQLAlchemy: {e}")
        return None
    finally:
        session.close()

def get_drug_index(drug_name):
    """Fetch the index of a drug from the top196drugs_transformed table."""
    cache_key = f"drug_index:{drug_name}"
    cached = redis_client.get(cache_key)
    if cached:
        return pickle.loads(cached)

    try:
        session = Session()
        query = text("""
            SELECT drug_id
            FROM top196drugs_transformed 
            WHERE drug_name = :drug_name
        """)
        result = session.execute(query, {'drug_name': drug_name}).fetchone()
        value = result[0] if result else None
        cache_result(cache_key, value)
        return value
    except Exception as e:
        print(f"Error fetching drug index from MariaDB: {e}")
        return None
    finally:
        session.close()

def values_for(drug1, drug2):
    """Fetch interaction values for two drugs from their respective transformed tables."""
    cache_key = f"interaction_values:{drug1}:{drug2}"
    cached = redis_client.get(cache_key)
    if cached:
        return pickle.loads(cached)

    feature_tables = [
        "MACCS_196_transformed",
        "RWsim_196_transformed",
        "fingerprint_sim_196_transformed",
        "feat_sim_196_transformed",
        "smiles_sim_196_transformed"
    ]

    values = {}
    drug1 = get_drug_index(drug1)
    drug2 = get_drug_index(drug2)
    if drug1 is None or drug2 is None:
        return {"error": "One or both drug IDs not found."}
    
    
    try:
        session = Session()
        for table in feature_tables:
            feature_name = table.replace("_transformed", "")
            query = text(f"""
                SELECT interaction_value 
                FROM {table} 
                WHERE (first_drug_id = :drug1 AND second_drug_id = :drug2) or (first_drug_id = :drug2 AND second_drug_id = :drug1)
            """)
            result = session.execute(query, {'drug1': drug1, 'drug2': drug2}).fetchone()
            values[feature_name] = result[0] if result else None

        cache_result(cache_key, values)
        return values
    except Exception as e:
        print(f"Error querying MariaDB via SQLAlchemy: {e}")
        return {"error": str(e)}
    finally:
        session.close()
