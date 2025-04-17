"""
TODO:
Model info display: Show description or last trained date for each model.
Auto-suggest for drug names: Enable AJAX-based suggestions in the frontend.
API versioning: Prefix /api/v1/airflow etc., for better scalability.
"""


from flask import Flask, request, render_template, make_response
from mlflow_client import list_models, predict_interaction
from airflow_client import trigger_ingestion, trigger_transformation, trigger_training, unpause_all_dags, pause_all_dags, is_dags_unpaused
from mariadb_client import get_all_drug_names, values_for
import json

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    models = list_models()
    drug_names = get_all_drug_names() or []
    prediction = None
    previous_data = request.cookies.get('previous_input')
    previous_input = json.loads(previous_data) if previous_data else {}

    history_data = request.cookies.get('prediction_history')
    prediction_history = json.loads(history_data) if history_data else []

    if request.method == 'POST':
        selected_model = request.form['model']
        input_data = {
            'MACCS_196': request.form.get('MACCS_196'),
            'RWsim_196': request.form.get('RWsim_196'),
            'fingerprint_sim_196': request.form.get('fingerprint_sim_196'),
            'feat_sim_196': request.form.get('feat_sim_196'),
            'smiles_sim_196': request.form.get('smiles_sim_196'),
        }
        try:
            features = [float(v) for v in input_data.values()]
        except (ValueError, TypeError) as e:
            return render_template('index.html', error="Invalid input data.", drug_names=drug_names, prediction=prediction, models=models, dags_unpaused=is_dags_unpaused())

        prediction = predict_interaction(selected_model, [features])

        history_entry = {**input_data, 'prediction': prediction}
        prediction_history.append(history_entry)
        
        # Store form data in a cookie
        response = make_response(render_template(
            'index.html', models=models, drug_names=drug_names, prediction=prediction, previous_input=request.form, prediction_history=prediction_history, dags_unpaused=is_dags_unpaused()
        ))
        response.set_cookie('previous_input', json.dumps(request.form))
        response.set_cookie('prediction_history', json.dumps(prediction_history))
        return response

    return render_template('index.html', models=models, drug_names=drug_names, prediction=prediction, previous_input=previous_input, prediction_history=prediction_history, dags_unpaused=is_dags_unpaused())

@app.route('/mariadb', methods=['POST'])
def mariadb():
    return values_for(request.json.get('drug1'), request.json.get('drug2'))

@app.route('/airflow', methods=['POST'])
def airflow():
    action = request.json.get('action')
    print(f"Received action: {action}")
    if action == 'trigger_ingestion':
        return trigger_ingestion()
    elif action == 'trigger_transformation':
        return trigger_transformation()
    elif action == 'trigger_training':
        return trigger_training()
    elif action == 'unpause_all_dags':
        return unpause_all_dags()
    elif action == 'pause_all_dags':
        return pause_all_dags()
    else:
        return {"error": "Invalid action"}, 400
    

@app.route('/clear-history', methods=['POST'])
def clear_history():
    response = make_response('', 302)
    response.headers["Location"] = "/"
    response.set_cookie('prediction_history', '', expires=0)
    response.set_cookie('previous_input', '', expires=0)
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050, debug=True)
