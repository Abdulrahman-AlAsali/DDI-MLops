# 🌐 Application Interface

This document explains the application interface stage of the DDI-MLops pipeline, detailing what the Flask API does, why it's needed, and how it was implemented.

## The What

### What is the Application Interface?

The application interface refers to the Flask-based API that enables users or external systems to interact with the DDI-MLops pipeline. It provides a web interface and an endpoint to handle requests.

### Key Components and Concepts
- **Flask**: A lightweight Python web framework used to build the API.
- **Endpoint**: Handles incoming requests and returns appropriate responses.
- **Jinja**: A template library that allow dynamic rendering of frontend websites.


### Input Dependencies
- **Request Type**: `GET` to request a webpage or a `POST` to request or send data to an endpoint  
- **Request Data**: For `POST` request, a JSON payload.


### Request Flow:
1. Flask receives a request.
2. If the request is a `GET` request, it returns the requested webpage
3. If the request is a `POST` request, request is handled and the appropriate response is sent back

### Expected Output
- Webpage or a JSON-formatted response.
- HTTP Status Codes (e.g 200, 400 or 500)


## The Why

### Why is this Stage Important?
- **User Access**: Enables users to interact with the system easily.
- **System Integration**: APIs allow the application to integrate into broader systems such as healthcare or drug development platforms.

### Why the Chosen Components Matter?

- **Flask**: Simple, lightweight, and suited well for building APIs.
- **Jinja**: To allow for generation of dynamic content for web applications. 

# The How

## Implementation Steps
1. Create API routes to handle requests
2. Response correctly to the request

## Code Example:

### `GET` request example
``` python
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html', models=models, drug_names=drug_names, prediction=prediction, previous_input=previous_input, prediction_history=prediction_history, dags_unpaused=is_dags_unpaused())
```

### `POST` request example
``` python
@app.route('/mariadb', methods=['POST'])
def mariadb():
    return values_for(request.json.get('drug1'), request.json.get('drug2'))
```

### Jinja example
``` xhtml
{% if prediction %}
<ul class="list-disc pl-4">
    {% for p in prediction %}
    <li>{{ p }}</li>
    {% endfor %}
</ul>
{% else %}
<span class="text-gray-500 italic">No prediction yet</span>
{% endif %}                            
```

# Related Page
- [Data ingestion](data_ingestion.md)
- [Data transformation](data_transformation.md)
- [Model training](model_training.md)
- [Caching](caching.md)
- [Application interface](application_interface.md)

# [GO to main page](../README.md)