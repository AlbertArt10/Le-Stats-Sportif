"""Modulul definește rutele API ale serverului Flask și logica pentru procesarea asincronă."""

import os
import json

from flask import request, jsonify
from app import webserver

@webserver.route('/api/post_endpoint', methods=['POST'])
def post_endpoint():
    """Endpoint de test simplu care returnează datele primite într-un request POST."""
    # Logăm intrarea și parametrii request-ului
    webserver.logger.info("Intrare în /api/post_endpoint, request: %s", request.json)
    if request.method == 'POST':
        # Presupunem că request-ul conține date JSON
        data = request.json
        # Procesăm datele primite (echo)
        response = {"message": "Received data successfully", "data": data}
        # Logăm ieșirea și răspunsul
        webserver.logger.info("Iesire din /api/post_endpoint, raspuns: %s", response)
        # Returnăm răspunsul ca JSON
        return jsonify(response)
    else:
        # Metodă neacceptată: logăm eroarea și returnăm un răspuns de eroare
        webserver.logger.error("Metoda neacceptată în /api/post_endpoint: %s", request.method)
        return jsonify({"error": "Method not allowed"}), 405


@webserver.route('/api/get_results/<job_id>', methods=['GET'])
def get_response(job_id):
    """Returnează rezultatul asociat unui job dacă este gata, altfel statusul 'running'."""
    # Logăm intrarea și verificăm job_id-ul
    webserver.logger.info("Intrare în /api/get_results cu job_id: %s", job_id)
    with webserver.job_status_lock:
        if job_id not in webserver.job_status:
            return jsonify({"status": "error", "reason": "Invalid job_id"})

    # Construim calea către fișierul de rezultat
    filename = f"results/{job_id}.json"

    # Verificăm dacă fișierul există
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            result_data = json.load(f)

        # Logăm ieșirea și datele rezultate
        webserver.logger.info("Job_id %s finalizat, date: %s", job_id, result_data)
        # Returnăm un răspuns JSON cu status-ul "done" și datele rezultate
        return jsonify({"status": "done", "data": result_data})
    else:
        # Dacă fișierul nu există, presupunem că job-ul este încă în curs de execuție
        webserver.logger.info("Job_id %s încă în execuție", job_id)
        return jsonify({"status": "running"})


def generate_job_id():
    """Generează un id unic pentru un job și setează statusul ca 'running'."""
    with webserver.job_status_lock:
        job_id = f"job_id_{webserver.job_counter}"
        webserver.job_status[job_id] = "running"
        webserver.job_counter += 1
    return job_id


def enqueue_job(job_id, func):
    """Adaugă un job în coadă și loghează acțiunea."""
    webserver.tasks_runner.job_queue.put(func)
    webserver.logger.info("Job-ul %s a fost adăugat în coadă", job_id)
    return jsonify({"job_id": job_id})


@webserver.route('/api/states_mean', methods=['POST'])
def states_mean_request():
    """Creează un job pentru calculul mediei pe state."""

    # Extragem datele din request-ul JSON
    data = request.json
    webserver.logger.info("Intrare în /api/states_mean, request: %s", data)

    job_id = generate_job_id()

    # Definim jobul ca o funcție ce calculează media pe state
    def job():
        result = webserver.data_ingestor.compute_states_mean(data['question'])
        return result, job_id

    # Adăugăm job-ul în coada de job-uri pentru execuție și returnăm job_id-ul
    return enqueue_job(job_id, job)


@webserver.route('/api/state_mean', methods=['POST'])
def state_mean_request():
    """Creează un job pentru calculul mediei unui anumit stat."""

    data = request.json
    webserver.logger.info("Intrare în /api/state_mean, request: %s", data)

    # Verificăm dacă am primit atât question cât și state
    if 'question' not in data or 'state' not in data:
        webserver.logger.error("Parametri lipsă în /api/state_mean: %s", data)
        return jsonify({"status": "error", "reason":
                            "Missing 'question' or 'state' parameter"}), 400

    # Generăm un job_id unic și setăm statusul "running"
    job_id = generate_job_id()

    # Definim jobul ca o funcție ce calculează media pentru state-ul specificat
    def job():
        result = webserver.data_ingestor.compute_state_mean(data['question'], data['state'])
        return result, job_id

    # Adăugăm job-ul în coada de job-uri pentru execuție și returnăm job_id-ul
    return enqueue_job(job_id, job)


@webserver.route('/api/best5', methods=['POST'])
def best5_request():
    """Creează un job pentru identificarea celor mai bune 5 state."""

    data = request.json
    webserver.logger.info("Intrare în /api/best5, request: %s", data)

    # Generăm un job_id unic și setăm statusul "running"
    job_id = generate_job_id()

    def job():
        # Calculăm cele mai bune 5 rezultate pe baza întrebării primite
        result = webserver.data_ingestor.compute_best5(data['question'])
        return result, job_id

    # Adăugăm job-ul în coada de job-uri pentru execuție și returnăm job_id-ul
    return enqueue_job(job_id, job)


@webserver.route('/api/worst5', methods=['POST'])
def worst5_request():
    """Creează un job pentru identificarea celor mai slabe 5 state."""

    # Extragem datele din request
    data = request.json
    webserver.logger.info("Intrare în /api/worst5, request: %s", data)

    # Generăm un job_id unic și setăm statusul "running"
    job_id = generate_job_id()

    def job():
        # Calculăm cele mai slabe 5 state pe baza întrebării
        result = webserver.data_ingestor.compute_worst5(data['question'])
        return result, job_id

    # Adăugăm job-ul în coada de job-uri pentru execuție și returnăm job_id-ul
    return enqueue_job(job_id, job)


@webserver.route('/api/global_mean', methods=['POST'])
def global_mean_request():
    """Creează un job pentru calcularea mediei globale."""

    data = request.json
    webserver.logger.info("Intrare în /api/global_mean, request: %s", data)

    # Generăm un job_id unic și setăm statusul "running"
    job_id = generate_job_id()

    # Definim job-ul pentru calculul mediei globale
    def job():
        result = webserver.data_ingestor.compute_global_mean(data['question'])
        return result, job_id

    # Adăugăm job-ul în coada de job-uri pentru execuție și returnăm job_id-ul
    return enqueue_job(job_id, job)


@webserver.route('/api/diff_from_mean', methods=['POST'])
def diff_from_mean_request():
    """Creează un job pentru calcularea diferenței dintre fiecare stat și media globală."""

    data = request.json
    webserver.logger.info("Intrare în /api/diff_from_mean, request: %s", data)

    # Verificăm dacă am primit "question"
    if 'question' not in data:
        webserver.logger.error("Parametru 'question' lipsă în /api/diff_from_mean")
        return jsonify({"status": "error", "reason": "Missing 'question' parameter"}), 400

    # Generăm un job_id unic și setăm statusul "running"
    job_id = generate_job_id()

    # Definim job-ul pentru calculul diferenței față de media globală
    def job():
        result = webserver.data_ingestor.compute_diff_from_mean(data['question'])
        return result, job_id

    # Adăugăm job-ul în coada de job-uri pentru execuție și returnăm job_id-ul
    return enqueue_job(job_id, job)


@webserver.route('/api/state_diff_from_mean', methods=['POST'])
def state_diff_from_mean_request():
    """Creează un job pentru diferența între un stat și media globală."""

    # Extragem datele din request
    data = request.json
    webserver.logger.info("Intrare în /api/state_diff_from_mean, request: %s", data)

    # Verificăm dacă s-au primit parametrii "question" și "state"
    if 'question' not in data or 'state' not in data:
        webserver.logger.error("Parametri lipsă în /api/state_diff_from_mean: %s", data)
        return jsonify({"status": "error", "reason":
                            "Missing 'question' or 'state' parameter"}), 400

    # Generăm un job_id unic și setăm statusul "running"
    job_id = generate_job_id()

    # Definim job-ul pentru calcularea diferenței între media globală și media statului
    def job():
        result = webserver.data_ingestor.compute_state_diff_from_mean(
                data['question'], data['state'])
        return result, job_id

    # Adăugăm job-ul în coada de job-uri pentru execuție și returnăm job_id-ul
    return enqueue_job(job_id, job)


@webserver.route('/api/mean_by_category', methods=['POST'])
def mean_by_category_request():
    """Creează un job pentru calculul mediei pe categorii."""

    # Extragem datele din request
    data = request.json
    webserver.logger.info("Intrare în /api/mean_by_category, request: %s", data)

    # Verificăm dacă parametrul "question" a fost primit
    if 'question' not in data:
        webserver.logger.error("Parametru 'question' lipsă în /api/mean_by_category")
        return jsonify({"status": "error", "reason": "Missing 'question' parameter"}), 400

    # Generăm un job_id unic și setăm statusul "running"
    job_id = generate_job_id()

    # Definim job-ul pentru calcularea mediei pe categorii
    def job():
        result = webserver.data_ingestor.compute_mean_by_category(data['question'])
        return result, job_id

    # Adăugăm job-ul în coada de job-uri pentru execuție și returnăm job_id-ul
    return enqueue_job(job_id, job)


@webserver.route('/api/state_mean_by_category', methods=['POST'])
def state_mean_by_category_request():
    """Creează un job pentru media pe categorii într-un anumit stat."""

    # Extragem datele din request
    data = request.json
    webserver.logger.info("Intrare în /api/state_mean_by_category, request: %s", data)

    # Validăm existența parametrilor "question" și "state"
    if 'question' not in data or 'state' not in data:
        webserver.logger.error("Parametri lipsă în /api/state_mean_by_category: %s", data)
        return jsonify({"status": "error", "reason":
                            "Missing 'question' or 'state' parameter"}), 400

    # Generăm un job_id unic și setăm statusul "running"
    job_id = generate_job_id()

    # Definim job-ul pentru calcularea mediei pe categorii pentru statul specificat
    def job():
        result = webserver.data_ingestor.compute_state_mean_by_category(
            data['question'], data['state'])
        return result, job_id

    # Adăugăm job-ul în coada de job-uri pentru execuție și returnăm job_id-ul
    return enqueue_job(job_id, job)


# Endpoint pentru index
@webserver.route('/')
@webserver.route('/index')
def index():
    """Returnează un mesaj de întâmpinare cu lista de rute disponibile."""
    routes = get_defined_routes()
    msg = "Hello, World!\n Interact with the webserver using one of the defined routes:\n"
    paragraphs = ""
    paragraphs = ''.join(f"<p>{route}</p>" for route in routes)
    msg += paragraphs
    return msg


def get_defined_routes():
    """Returnează lista rutelor definite în aplicație."""
    routes = []
    for rule in webserver.url_map.iter_rules():
        methods = ', '.join(rule.methods)
        routes.append(f"Endpoint: \"{rule}\" Methods: \"{methods}\"")
    return routes


@webserver.route('/api/graceful_shutdown', methods=['GET'])
def graceful_shutdown():
    """Semnalează închiderea serverului și returnează statusul execuției joburilor."""

    # Semnalăm ThreadPool-ului că nu se mai acceptă joburi noi
    webserver.tasks_runner.shutdown_event.set()
    webserver.logger.info("Shutdown semnalat, verificăm coada de joburi.")

    # Verificăm dacă coada este goală
    if webserver.tasks_runner.job_queue.empty():
        webserver.logger.info("Coada de joburi este goală, shutdown finalizat.")
        return jsonify({"status": "done"})
    else:
        webserver.logger.info("Coada de joburi nu este goală, status: running.")
        return jsonify({"status": "running"})


@webserver.route('/api/jobs', methods=['GET'])
def jobs():
    """Returnează statusul curent al tuturor joburilor procesate sau în curs."""

    webserver.logger.info("Endpoint-ul /api/jobs accesat, job_status: %s", webserver.job_status)
    with webserver.job_status_lock:
        return jsonify({"status": "done", "data": dict(webserver.job_status)})


@webserver.route('/api/num_jobs', methods=['GET'])
def num_jobs():
    """Returnează numărul de joburi rămase în coada de execuție."""

    remaining = webserver.tasks_runner.job_queue.qsize()
    webserver.logger.info("Endpoint-ul /api/num_jobs accesat, joburi rămase: %d", remaining)
    return jsonify({"num_jobs": remaining})
