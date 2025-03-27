from queue import Queue
from threading import Thread, Event
import time
import os

class ThreadPool:
    def __init__(self):
        # You must implement a ThreadPool of TaskRunners
        # Your ThreadPool should check if an environment variable TP_NUM_OF_THREADS is defined
        # If the env var is defined, that is the number of threads to be used by the thread pool
        # Otherwise, you are to use what the hardware concurrency allows
        # You are free to write your implementation as you see fit, but
        # You must NOT:
        #   * create more threads than the hardware concurrency allows
        #   * recreate threads for each task
        # Note: the TP_NUM_OF_THREADS env var will be defined by the checker
        
        # Determinăm numărul de threaduri
        num_threads = int(os.environ.get("TP_NUM_OF_THREADS", os.cpu_count()))
        self.job_queue = Queue()
        self.workers = []
        for _ in range(num_threads):
            worker = TaskRunner(self.job_queue)
            worker.start()
            self.workers.append(worker)

class TaskRunner(Thread):
    def __init__(self, job_queue):
        Thread.__init__(self)
        self.job_queue = job_queue
        self.daemon = True  # Permite închiderea threadurilor la exit

    def run(self):
        while True:
            job = self.job_queue.get()
            try:
                # Executăm jobul (job e o funcție)
                result, job_id = job()
                # Salvăm rezultatul pe disc, de exemplu într-un fișier cu numele job_id în directorul "results/"
                with open(f"results/{job_id}.json", "w") as f:
                    import json
                    json.dump(result, f)
            except Exception as e:
                print(f"Eroare la execuția jobului: {e}")
            finally:
                self.job_queue.task_done()
