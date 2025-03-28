from queue import Queue, Empty
from threading import Thread, Event
import time
import os
import json

class ThreadPool:
    def __init__(self, webserver):

        # Determinăm numărul de threaduri
        num_threads = int(os.environ.get("TP_NUM_OF_THREADS", os.cpu_count()))
        self.webserver = webserver
        self.job_queue = Queue()
        self.shutdown_event = Event()  # Semnal de shutdown
        self.workers = []
        for _ in range(num_threads):
            worker = TaskRunner(self.job_queue, self.shutdown_event, self.webserver)
            worker.start()
            self.workers.append(worker)

class TaskRunner(Thread):
    def __init__(self, job_queue, shutdown_event, webserver):
        Thread.__init__(self)
        self.job_queue = job_queue
        self.shutdown_event = shutdown_event
        self.webserver = webserver
        self.daemon = True  # Permite închiderea threadurilor la exit

    def run(self):
        while True:
            try:
                job = self.job_queue.get(timeout=1)
            except Empty:
                if self.shutdown_event.is_set() and self.job_queue.empty():
                    break  # Ieșim din loop dacă s-a semnalat shutdown și nu mai sunt joburi
                continue

            try:
                # Executăm funcția job()
                result, job_id = job()
                # Salvăm rezultatul pe disc
                with open(f"results/{job_id}.json", "w") as f:
                    json.dump(result, f)
                self.webserver.job_status[job_id] = "done"  # Actualizăm statusul la done

            except Exception as e:
                self.webserver.logger.error("Eroare la execuția jobului: %s", e)
                self.webserver.job_status[job_id] = "error"
            finally:
                self.job_queue.task_done()
