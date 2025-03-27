from app import webserver
from flask import request, jsonify

import os
import json

# Example endpoint definition
# Endpoint de test simplu: echo
@webserver.route('/api/post_endpoint', methods=['POST'])
def post_endpoint():
    if request.method == 'POST':
        # Assuming the request contains JSON data
        data = request.json
        print(f"got data in post {data}")

        # Process the received data
        # For demonstration purposes, just echoing back the received data
        response = {"message": "Received data successfully", "data": data}

        # Sending back a JSON response
        return jsonify(response)
    else:
        # Method Not Allowed
        return jsonify({"error": "Method not allowed"}), 405

# Endpoint pentru obținerea rezultatelor unui job
@webserver.route('/api/get_results/<job_id>', methods=['GET'])
def get_response(job_id):
    print(f"JobID is {job_id}")
    # Construim calea către fișierul de rezultat
    filename = f"results/{job_id}.json"

    # Verificăm dacă fișierul există
    if os.path.exists(filename):
        with open(filename, "r") as f:
            result_data = json.load(f)
        # Returnăm un răspuns JSON cu status-ul "done" și datele rezultate
        return jsonify({"status": "done", "data": result_data})
    else:
        # Dacă fișierul nu există, presupunem că job-ul este încă în curs de execuție
        return jsonify({"status": "running"})


# Endpoint pentru calculul mediei pe state
@webserver.route('/api/states_mean', methods=['POST'])
def states_mean_request():
    # Extragem datele din request-ul JSON
    data = request.json
    print(f"Got request {data}")
    
    # Generăm un job_id unic
    current_job_id = webserver.job_counter
    webserver.job_counter += 1

    # Definim jobul ca o funcție ce calculează media pe state
    def job():
        result = webserver.data_ingestor.compute_states_mean(data['question'])
        return result, f"job_id_{current_job_id}"
    
    # Adăugăm jobul în coada ThreadPool-ului
    webserver.tasks_runner.job_queue.put(job)
    
    # Returnăm job_id-ul către client
    return jsonify({"job_id": f"job_id_{current_job_id}"})


@webserver.route('/api/state_mean', methods=['POST'])
def state_mean_request():
    data = request.json
    print(f"Got request {data}")
    
    # Verificăm dacă am primit atât question cât și state
    if 'question' not in data or 'state' not in data:
        return jsonify({"status": "error", "reason": "Missing 'question' or 'state' parameter"}), 400
    
    # Generăm un job_id unic
    current_job_id = webserver.job_counter
    webserver.job_counter += 1
    
    # Definim jobul ca o funcție ce calculează media pentru state-ul specificat
    def job():
        result = webserver.data_ingestor.compute_state_mean(data['question'], data['state'])
        return result, f"job_id_{current_job_id}"
    
    # Adăugăm jobul în coada de job-uri pentru execuție
    webserver.tasks_runner.job_queue.put(job)

    # Returnăm job_id-ul către client
    return jsonify({"job_id": f"job_id_{current_job_id}"})


@webserver.route('/api/best5', methods=['POST'])
def best5_request():
    data = request.json
    print(f"Got request {data}")
    
    # Generăm un job_id unic
    current_job_id = webserver.job_counter
    webserver.job_counter += 1

    def job():
        # Calculăm cele mai bune 5 rezultate pe baza întrebării primite
        result = webserver.data_ingestor.compute_best5(data['question'])
        return result, f"job_id_{current_job_id}"

    # Adăugăm job-ul în coada
    webserver.tasks_runner.job_queue.put(job)

    # Returnăm job_id-ul către client
    return jsonify({"job_id": f"job_id_{current_job_id}"})


@webserver.route('/api/worst5', methods=['POST'])
def worst5_request():
    # TODO
    # Get request data
    # Register job. Don't wait for task to finish
    # Increment job_id counter
    # Return associated job_id

    return jsonify({"status": "NotImplemented"})

@webserver.route('/api/global_mean', methods=['POST'])
def global_mean_request():
    # TODO
    # Get request data
    # Register job. Don't wait for task to finish
    # Increment job_id counter
    # Return associated job_id

    return jsonify({"status": "NotImplemented"})

@webserver.route('/api/diff_from_mean', methods=['POST'])
def diff_from_mean_request():
    # TODO
    # Get request data
    # Register job. Don't wait for task to finish
    # Increment job_id counter
    # Return associated job_id

    return jsonify({"status": "NotImplemented"})

@webserver.route('/api/state_diff_from_mean', methods=['POST'])
def state_diff_from_mean_request():
    # TODO
    # Get request data
    # Register job. Don't wait for task to finish
    # Increment job_id counter
    # Return associated job_id

    return jsonify({"status": "NotImplemented"})

@webserver.route('/api/mean_by_category', methods=['POST'])
def mean_by_category_request():
    # TODO
    # Get request data
    # Register job. Don't wait for task to finish
    # Increment job_id counter
    # Return associated job_id

    return jsonify({"status": "NotImplemented"})

@webserver.route('/api/state_mean_by_category', methods=['POST'])
def state_mean_by_category_request():
    # TODO
    # Get request data
    # Register job. Don't wait for task to finish
    # Increment job_id counter
    # Return associated job_id

    return jsonify({"status": "NotImplemented"})


# Endpoint pentru index – afișează rutele definite
@webserver.route('/')
@webserver.route('/index')
def index():
    routes = get_defined_routes()
    msg = "Hello, World!\n Interact with the webserver using one of the defined routes:\n"
    paragraphs = ""
    for route in routes:
        paragraphs += f"<p>{route}</p>"
    msg += paragraphs
    return msg


def get_defined_routes():
    routes = []
    for rule in webserver.url_map.iter_rules():
        methods = ', '.join(rule.methods)
        routes.append(f"Endpoint: \"{rule}\" Methods: \"{methods}\"")
    return routes
