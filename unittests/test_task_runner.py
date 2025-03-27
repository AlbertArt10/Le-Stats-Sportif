import os
import time
import json
from app.task_runner import ThreadPool

# Definim un job simplu care va returna un rezultat și un job_id.
def test_job():
    # De exemplu, jobul nostru returnează o valoare fixă.
    return {"result": 42}, "job_test"

# Creăm un ThreadPool
pool = ThreadPool()

# Adăugăm jobul în coada de joburi.
pool.job_queue.put(test_job)

# Așteptăm până când joburile sunt procesate.
pool.job_queue.join()

# Verificăm dacă fișierul cu rezultatul jobului a fost creat în directorul "results/".
job_file = "results/job_test.json"
if os.path.exists(job_file):
    with open(job_file, "r") as f:
        data = json.load(f)
    print("Job procesat cu succes. Rezultat:", data)
else:
    print("Fișierul jobului nu a fost găsit!")
