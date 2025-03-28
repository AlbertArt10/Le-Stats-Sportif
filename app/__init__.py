import os
from flask import Flask
from threading import Lock
from app.data_ingestor import DataIngestor
from app.task_runner import ThreadPool
from app.logger_setup import setup_logger

if not os.path.exists('results'):
    os.mkdir('results')

webserver = Flask(__name__)
webserver.tasks_runner = ThreadPool(webserver)

webserver.data_ingestor = DataIngestor("./nutrition_activity_obesity_usa_subset.csv")

webserver.job_counter = 1
webserver.job_status = {}

webserver.job_counter_lock = Lock()
webserver.job_status_lock = Lock()

# webserver.logger = setup_logger()

from app import routes
