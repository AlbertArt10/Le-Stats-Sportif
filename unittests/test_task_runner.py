import unittest
import os
import json
from app.task_runner import ThreadPool
from app import webserver

class TestTaskRunner(unittest.TestCase):
    def test_job_execution(self):
        # Cream un nou ThreadPool pentru test
        pool = ThreadPool(webserver)
        # Definim un job simplu care returnează un rezultat fix
        def test_job():
            return {"result": 42}, "job_test"
        # Adăugăm jobul în coadă
        pool.job_queue.put(test_job)
        # Așteptăm ca jobul să fie procesat
        pool.job_queue.join()
        # Verificăm că fișierul cu rezultatul jobului a fost creat
        job_file = "results/job_test.json"
        self.assertTrue(os.path.exists(job_file), "Fișierul rezultat pentru job nu a fost găsit")
        with open(job_file, "r") as f:
            data = json.load(f)
        self.assertEqual(data, {"result": 42}, "Rezultatul jobului nu corespunde")
        # Ștergem fișierul de test
        os.remove(job_file)

if __name__ == '__main__':
    unittest.main()
