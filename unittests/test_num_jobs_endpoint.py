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
        # Definim un job dummy care returnează rapid
        def dummy_job():
            return {"result": "dummy"}, "dummy_job"

        # Adăugăm câteva joburi dummy în coadă
        for _ in range(3):
            webserver.tasks_runner.job_queue.put(dummy_job)

        # Simulăm apelul endpoint-ului de graceful shutdown
        with webserver.test_client() as client:
            response_shutdown = client.get('/api/graceful_shutdown')
            self.assertEqual(response_shutdown.status_code, 200)

            # Verificăm că shutdown-ul a fost semnalat
            self.assertTrue(webserver.tasks_runner.shutdown_event.is_set())

            # Verificăm că mai există joburi rămase în coadă (pentru că n-au fost procesate)
            remaining_jobs = webserver.tasks_runner.job_queue.qsize()
            self.assertGreater(remaining_jobs, 0, "Ne așteptam ca joburi să fie încă în coadă după shutdown")

            # Apelăm endpoint-ul pentru numărul de joburi
            response_num_jobs = client.get('/api/num_jobs')
            self.assertEqual(response_num_jobs.status_code, 200)
            data = response_num_jobs.get_json()

            self.assertEqual(data.get("num_jobs"), remaining_jobs, "Numărul raportat de joburi nu corespunde cu ce e în coadă")


if __name__ == '__main__':
    unittest.main()
