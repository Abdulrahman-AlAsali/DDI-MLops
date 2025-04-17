# 🧠 Caching

This document outlines the caching stage of the DDI-MLops pipeline, describing what caching is, why it's critical for performance, and how it was implemented using Redis.

## The What

### What is Caching?

Caching is the process of temporarily storing frequently accessed data in a fast-access storage layer to avoid repeated computations or database lookups. In the context of this project, caching is used to store API querry results such as prediction inferences, reducing response time and database load.

### Key Components and Concepts
- **Redis**: An Key-Value in-memory data store used as a high-performance cache.
- **Flask API**: The application checks the Redis cache before querying or inferencing.

### Input Dependencies
- **A Request**: is made via the Flask API to query or inferences.
- **Cache Key**: an identifier for the value stored in the Redis


### Data Access Flow:
1. Flask receives a request.
2. It constructs a cache key based on the request.
3. Checks Redis for the cache key.
4. If cached, returns it instantly; if not, queries or inferences based on the request and then stores it in Redis.

### Expected Output
- Immediate responses for repeated queries.
- Reduced database query and model inference load.

## The Why

### Why is this Stage Important?
- **Efficiency**: Minimises unnecessary model inferences and database hits.

### Why Redis?

- **Speed**: In-memory data access is faster than database or file-based storage.
- **Docker Compatible**: Easily runs in a containerised environment with nearly no configuration
- **Simplicity**: Lightweight setup

# The How

## Implementation Steps
1. Connect to Redis
2. Format the key for the request
3. Look up the key in Redis
4. If the key is in Redis then return the cached value
5. If the key is not in Redis then do the request then store the value in Redis  

## Code Example:
``` python
def list_models(): 
    cached_models = redis_client.get("model_list")
    if cached_models:
        # if models are cached
        return cached_models
    
    # If models are not cached (not in Redis)
    models = ...

    redis_client.set("model_list", json.dumps(models), ex=60 * 60)

    return models
```


# Related Page
- [Data ingestion](data_ingestion.md)
- [Data transformation](data_transformation.md)
- [Model training](model_training.md)
- [Caching](caching.md)
- [Application interface](application_interface.md)

# [GO to main page](../README.md)