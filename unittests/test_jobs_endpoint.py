import unittest
from app import webserver

class TestJobsEndpoint(unittest.TestCase):
    def setUp(self):
        # Resetăm dicționarul de joburi înainte de fiecare test
        webserver.job_status = {}
        # Pre-populăm cu câteva valori de test:
        webserver.job_status["job_id_1"] = "done"
        webserver.job_status["job_id_2"] = "running"
        webserver.job_status["job_id_3"] = "running"

    def test_jobs_endpoint(self):
        with webserver.test_client() as client:
            response = client.get('/api/jobs')
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            # Verificăm că statusul global este "done"
            self.assertEqual(data.get("status"), "done")
            # Verificăm că "data" conține exact joburile și statusurile așteptate
            expected = {
                "job_id_1": "done",
                "job_id_2": "running",
                "job_id_3": "running"
            }
            self.assertEqual(data.get("data"), expected)

if __name__ == '__main__':
    unittest.main()
