"""Inițializează aplicația Flask, loggerul, thread pool-ul și încarcă datele CSV."""

import os
from threading import Lock  # standard lib
from flask import Flask  # third-party

from app.data_ingestor import DataIngestor
from app.task_runner import ThreadPool
from app.logger_setup import setup_logger

# Creăm folderul pentru rezultate dacă nu există deja
if not os.path.exists('results'):
    os.mkdir('results')

# Inițializăm aplicația Flask
webserver = Flask(__name__)

# Inițializăm loggerul aplicației
# webserver.logger = setup_logger()

# Inițializăm thread pool-ul cu referință la webserver
webserver.tasks_runner = ThreadPool(webserver)

# Încărcăm datele din fișierul CSV
webserver.data_ingestor = DataIngestor("./nutrition_activity_obesity_usa_subset.csv")

# Inițializăm contorul de joburi și structura de status
webserver.job_counter = 1
webserver.job_status = {}

# Lock-uri pentru acces concurent
webserver.job_counter_lock = Lock()
webserver.job_status_lock = Lock()

# Importăm rutele definite
from app import routes  # pylint: disable=cyclic-import, wrong-import-position
