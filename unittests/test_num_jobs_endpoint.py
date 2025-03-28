import unittest
import time
from app import webserver

class TestNumJobsEndpoint(unittest.TestCase):
    def setUp(self):
        # Curățăm coada de joburi înainte de test
        while not webserver.tasks_runner.job_queue.empty():
            try:
                webserver.tasks_runner.job_queue.get_nowait()
            except Exception:
                break

    def test_num_jobs_after_shutdown(self):
        # Definim un job dummy care se termină rapid
        def dummy_job():
            return {"result": "dummy"}, "dummy_job"

        # Adăugăm câteva joburi dummy în coadă
        for _ in range(3):
            webserver.tasks_runner.job_queue.put(dummy_job)
        
        # Așteptăm ca joburile să fie procesate (folosim join pentru a bloca până când coada este goală)
        webserver.tasks_runner.job_queue.join()

        # Simulăm apelul endpoint-ului de graceful shutdown
        with webserver.test_client() as client:
            response_shutdown = client.get('/api/graceful_shutdown')
            self.assertEqual(response_shutdown.status_code, 200)
            # După shutdown, așteptăm puțin ca thread-urile să finalizeze orice job restant
            time.sleep(1)
            
            # Apelăm endpoint-ul /api/num_jobs pentru a verifica numărul de joburi rămase
            response_num_jobs = client.get('/api/num_jobs')
            self.assertEqual(response_num_jobs.status_code, 200)
            data = response_num_jobs.get_json()
            # Așteptăm ca numărul de joburi rămase să fie 0
            self.assertEqual(data.get("num_jobs"), 0, "Numărul de joburi rămase nu este 0 după shutdown și finalizarea joburilor.")

if __name__ == '__main__':
    unittest.main()
