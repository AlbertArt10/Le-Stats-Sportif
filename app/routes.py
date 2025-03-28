from app import webserver
from flask import request, jsonify

import os
import json

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

    # Verificăm dacă job_id este valid
    if job_id not in webserver.job_status:
        return jsonify({"status": "error", "reason": "Invalid job_id"})
    
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
    
    # Generăm un job_id unic și setăm statusul inițial "running"
    job_id = f"job_id_{webserver.job_counter}"
    webserver.job_status[job_id] = "running"
    webserver.job_counter += 1

    # Definim jobul ca o funcție ce calculează media pe state
    def job():
        result = webserver.data_ingestor.compute_states_mean(data['question'])
        return result, job_id
    
    # Adăugăm jobul în coada ThreadPool-ului
    webserver.tasks_runner.job_queue.put(job)
    
    # Returnăm job_id-ul către client
    return jsonify({"job_id": job_id})


# Endpoint pentru calculul mediei pentru un anumit stat
@webserver.route('/api/state_mean', methods=['POST'])
def state_mean_request():
    data = request.json
    print(f"Got request {data}")
    
    # Verificăm dacă am primit atât question cât și state
    if 'question' not in data or 'state' not in data:
        return jsonify({"status": "error", "reason": "Missing 'question' or 'state' parameter"}), 400
    
    # Generăm un job_id unic și setăm statusul "running"
    job_id = f"job_id_{webserver.job_counter}"
    webserver.job_status[job_id] = "running"
    webserver.job_counter += 1
    
    # Definim jobul ca o funcție ce calculează media pentru state-ul specificat
    def job():
        result = webserver.data_ingestor.compute_state_mean(data['question'], data['state'])
        return result, job_id
    
    # Adăugăm jobul în coada de job-uri pentru execuție
    webserver.tasks_runner.job_queue.put(job)

    # Returnăm job_id-ul către client
    return jsonify({"job_id": job_id})


# Endpoint pentru calculul best5
@webserver.route('/api/best5', methods=['POST'])
def best5_request():
    data = request.json
    print(f"Got request {data}")
    
    # Generăm un job_id unic și setăm statusul "running"
    job_id = f"job_id_{webserver.job_counter}"
    webserver.job_status[job_id] = "running"
    webserver.job_counter += 1

    def job():
        # Calculăm cele mai bune 5 rezultate pe baza întrebării primite
        result = webserver.data_ingestor.compute_best5(data['question'])
        return result, job_id

    # Adăugăm job-ul în coada
    webserver.tasks_runner.job_queue.put(job)

    # Returnăm job_id-ul către client
    return jsonify({"job_id": job_id})


# Endpoint pentru calculul worst5
@webserver.route('/api/worst5', methods=['POST'])
def worst5_request():
    # extragem datele din request
    data = request.json
    print(f"Got request {data}")
    
    # Generăm un job_id unic și setăm statusul "running"
    job_id = f"job_id_{webserver.job_counter}"
    webserver.job_status[job_id] = "running"
    webserver.job_counter += 1

    def job():
        # calculăm cele mai slabe 5 state pe baza întrebării
        result = webserver.data_ingestor.compute_worst5(data['question'])
        return result, job_id

    # adăugăm job-ul în coada ThreadPool-ului
    webserver.tasks_runner.job_queue.put(job)

    # returnăm job_id-ul către client
    return jsonify({"job_id": job_id})


# Endpoint pentru calculul mediei globale
@webserver.route('/api/global_mean', methods=['POST'])
def global_mean_request():
    # extragem datele primite în request
    data = request.json
    print(f"Got request {data}")
    
    # Generăm un job_id unic și setăm statusul "running"
    job_id = f"job_id_{webserver.job_counter}"
    webserver.job_status[job_id] = "running"
    webserver.job_counter += 1

    # definim job-ul pentru calculul mediei globale
    def job():
        result = webserver.data_ingestor.compute_global_mean(data['question'])
        return result, job_id

    # adăugăm job-ul în coada ThreadPool-ului
    webserver.tasks_runner.job_queue.put(job)

    # returnăm job_id-ul generat către client
    return jsonify({"job_id": job_id})


# Endpoint pentru calculul diferenței față de media globală
@webserver.route('/api/diff_from_mean', methods=['POST'])
def diff_from_mean_request():
    # extragem datele din request
    data = request.json
    print(f"Got request {data}")
    
    # Verificăm dacă am primit "question"
    if 'question' not in data:
        return jsonify({"status": "error", "reason": "Missing 'question' parameter"}), 400

    # Generăm un job_id unic și setăm statusul "running"
    job_id = f"job_id_{webserver.job_counter}"
    webserver.job_status[job_id] = "running"
    webserver.job_counter += 1

    # definim job-ul pentru calculul diferenței față de media globală
    def job():
        result = webserver.data_ingestor.compute_diff_from_mean(data['question'])
        return result, job_id

    # adăugăm job-ul în coada ThreadPool-ului
    webserver.tasks_runner.job_queue.put(job)
    # returnăm job_id-ul generat către client
    return jsonify({"job_id": job_id})


# Endpoint pentru calculul diferenței între media globală și media unui stat
@webserver.route('/api/state_diff_from_mean', methods=['POST'])
def state_diff_from_mean_request():
    # Extragem datele din request
    data = request.json
    print(f"Got request {data}")

    # Verificăm dacă s-au primit parametrii "question" și "state"
    if 'question' not in data or 'state' not in data:
        return jsonify({"status": "error", "reason": "Missing 'question' or 'state' parameter"}), 400

    # Generăm un job_id unic și setăm statusul "running"
    job_id = f"job_id_{webserver.job_counter}"
    webserver.job_status[job_id] = "running"
    webserver.job_counter += 1

    # Definim job-ul pentru calcularea diferenței între media globală și media statului
    def job():
        result = webserver.data_ingestor.compute_state_diff_from_mean(data['question'], data['state'])
        return result, job_id

    # Adăugăm job-ul în coada ThreadPool-ului
    webserver.tasks_runner.job_queue.put(job)
    # Returnăm job_id-ul generat către client
    return jsonify({"job_id": job_id})


# Endpoint pentru calculul mediei pe categorii
@webserver.route('/api/mean_by_category', methods=['POST'])
def mean_by_category_request():
    # Extragem datele din request
    data = request.json
    print(f"Got request {data}")
    # Verificăm dacă parametrul "question" a fost primit
    if 'question' not in data:
        return jsonify({"status": "error", "reason": "Missing 'question' parameter"}), 400

    # Generăm un job_id unic și setăm statusul "running"
    job_id = f"job_id_{webserver.job_counter}"
    webserver.job_status[job_id] = "running"
    webserver.job_counter += 1

    # Definim job-ul pentru calcularea mediei pe categorii
    def job():
        result = webserver.data_ingestor.compute_mean_by_category(data['question'])
        return result, job_id
    
    # Adăugăm job-ul în coada ThreadPool-ului
    webserver.tasks_runner.job_queue.put(job)
    # Returnăm job_id-ul generat către client
    return jsonify({"job_id": job_id})


# Endpoint pentru calculul mediei pe categorii pentru un stat anume
@webserver.route('/api/state_mean_by_category', methods=['POST'])
def state_mean_by_category_request():
    # Preluăm datele din request-ul JSON
    data = request.json
    print(f"Got request {data}")
    
    # Validăm existența parametrilor "question" și "state"
    if 'question' not in data or 'state' not in data:
        return jsonify({"status": "error", "reason": "Missing 'question' or 'state' parameter"}), 400

    # Generăm un job_id unic și setăm statusul "running"
    job_id = f"job_id_{webserver.job_counter}"
    webserver.job_status[job_id] = "running"
    webserver.job_counter += 1

    # Definim job-ul pentru calcularea mediei pe categorii pentru statul specificat
    def job():
        result = webserver.data_ingestor.compute_state_mean_by_category(data['question'], data['state'])
        return result, job_id
    
    # Adăugăm job-ul în coada de execuție a ThreadPool-ului
    webserver.tasks_runner.job_queue.put(job)
    # Returnăm job_id-ul generat către client
    return jsonify({"job_id": job_id})


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


# Endpoint pentru graceful shutdown
@webserver.route('/api/graceful_shutdown', methods=['GET'])
def graceful_shutdown():
    # Semnalăm ThreadPool-ului că nu se mai acceptă joburi noi
    webserver.tasks_runner.shutdown_event.set()
    # Verificăm dacă coada este goală
    if webserver.tasks_runner.job_queue.empty():
        return jsonify({"status": "done"})
    else:
        return jsonify({"status": "running"})


# Endpoint pentru listarea joburilor și a statusurilor lor
@webserver.route('/api/jobs', methods=['GET'])
def jobs():
    # Returnăm un JSON cu toate job_id-urile și statusurile lor
    return jsonify({"status": "done", "data": webserver.job_status})


# Endpoint pentru numărul de joburi rămase
@webserver.route('/api/num_jobs', methods=['GET'])
def num_jobs():
    # Returnăm numărul de joburi rămase în coadă
    remaining = webserver.tasks_runner.job_queue.qsize()
    return jsonify({"num_jobs": remaining})