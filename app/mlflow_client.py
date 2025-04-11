import hashlib
import tempfile
import zipfile
import json
import os
import shutil

import pandas as pd
import mlflow.pyfunc
import redis
from mlflow.tracking import MlflowClient

client = MlflowClient()
redis_client = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://redis:6379/0"), decode_responses=False)

class ModelWrapper(mlflow.pyfunc.PythonModel):
    def __init__(self, model):
        self.model = model

    def predict(self, context, model_input):
        return self.model.predict(model_input)

def _model_cache_key(model_name: str) -> str:
    return f"model:{model_name}"

def _prediction_cache_key(model_name: str, features_list: list) -> str:
    # Create a unique key based on the model name and features
    features_hash = hashlib.sha256(json.dumps(features_list, sort_keys=True).encode()).hexdigest()
    return f"prediction:{model_name}:{features_hash}"


# TODO: Add a function to store and load the model from the cache
def _load_model(model_name: str):
    # Check if the model is already cached
    cache_key = _model_cache_key(model_name)
    cached_model = redis_client.get(cache_key)
    print(f"checking Cache")
    if cached_model:
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = os.path.join(temp_dir, "model.zip")
            with open(zip_path, "wb") as f:
                f.write(cached_model)
            
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Ensure the extracted model is a valid PythonModel
            model = mlflow.pyfunc.load_model(temp_dir)
            return model
    print(f"Model not found in cache, loading from MLflow: {model_name}")
    # Load the model from MLflow
    model_uri = f"models:/{model_name}/latest"
    model = mlflow.pyfunc.load_model(model_uri)
    print(f"Loaded model from MLflow: {model_uri}")

    wrapped_model = ModelWrapper(model)
    print(f"Wrapped model: {model_uri}")
    # Save the model properly as a PythonModel
    with tempfile.TemporaryDirectory() as temp_dir:
        # Save the model with mlflow's save_model
        mlflow.pyfunc.save_model(path=temp_dir, python_model=wrapped_model)

        zip_path = os.path.join(temp_dir, "model.zip")
        shutil.make_archive(base_name=zip_path.replace('.zip',''), format='zip', root_dir=temp_dir)

        with open(zip_path, "rb") as f:
            model_data = f.read()

        redis_client.set(cache_key, model_data, ex=60 * 60 * 24)
    
    return wrapped_model


def list_models(): 
    cached_models = redis_client.get("model_list")
    if cached_models:
        models = json.loads(cached_models)
        if models:
            return models
    
    models = [model.name for model in client.search_registered_models()]

    redis_client.set("model_list", json.dumps(models), ex=60 * 60)

    return models


def predict_interaction(model_name, features_list):
    # try:
        print(f"Predicting with model: {model_name}")
        p_key = _prediction_cache_key(model_name, features_list)
        if (cached := redis_client.get(p_key)) is not None:
            return json.loads(cached)
        
        # Load the model from the Mlflow registry
        model = mlflow.pyfunc.load_model(f"models:/{model_name}/latest")

        # Convert input list to pandas DataFrame
        df = pd.DataFrame(
            features_list,
            columns=[
                "MACCS_196_transformed_score",
                "RWsim_196_transformed_score",
                "fingerprint_sim_196_transformed_score",
                "feat_sim_196_transformed_score",
                "smiles_sim_196_transformed_score"
            ]
        )

        # Predict
        predictions = model.predict(df)

        # Translate prediction values
        translated = []
        for p in predictions:
            if p == -1:
                translated.append("❌ No interaction will happen")
            elif p == 1:
                translated.append("✅ Interaction will happen")
            else:
                translated.append(f"ℹ️ Prediction: {p}")
        
        redis_client.set(p_key, json.dumps(translated), ex= 60 * 2)
        
        return translated

