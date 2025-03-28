import unittest
import os
import json
from app import webserver

class TestGetResultsEndpoint(unittest.TestCase):
    def setUp(self):
        # Resetăm dicționarul de joburi pentru test
        webserver.job_status = {}
        # Asigurăm existența directorului "results"
        if not os.path.exists("results"):
            os.mkdir("results")
    
    def tearDown(self):
        # Curățăm eventualele fișiere de test din directorul "results"
        for filename in os.listdir("results"):
            if filename.startswith("job_test_") or filename.startswith("job_id_"):
                os.remove(os.path.join("results", filename))
    
    def test_invalid_job_id(self):
        """
        Dacă job_id-ul nu este valid (nu începe cu "job_id_" sau nu se găsește în job_status),
        endpoint-ul trebuie să returneze:
        {
          "status": "error",
          "reason": "Invalid job_id"
        }
        """
        with webserver.test_client() as client:
            response = client.get('/api/get_results/invalid_job_id')
            data = response.get_json()
            self.assertEqual(data.get("status"), "error", f"Răspunsul a fost: {data}")
            self.assertEqual(data.get("reason"), "Invalid job_id")
    
    def test_running_job(self):
        """
        Dacă job_id-ul este valid, dar fișierul de rezultat nu există,
        endpoint-ul trebuie să returneze:
        {
          "status": "running"
        }
        """
        valid_job_id = "job_id_100"
        # Simulăm că avem un job valid dar care nu a finalizat:
        webserver.job_status[valid_job_id] = "running"
        # Ne asigurăm că nu există fișierul de rezultat
        result_file = f"results/{valid_job_id}.json"
        if os.path.exists(result_file):
            os.remove(result_file)
        
        with webserver.test_client() as client:
            response = client.get(f'/api/get_results/{valid_job_id}')
            data = response.get_json()
            self.assertEqual(data.get("status"), "running")
    
    def test_done_job(self):
        """
        Dacă job_id-ul este valid și rezultatul este gata (fișierul de rezultat există),
        endpoint-ul trebuie să returneze:
        {
          "status": "done",
          "data": <JSON_REZULTAT_PROCESARE>
        }
        """
        valid_job_id = "job_id_200"
        expected_result = {"result": "ok", "value": 123}
        # Simulăm că jobul a terminat:
        webserver.job_status[valid_job_id] = "done"
        result_file = f"results/{valid_job_id}.json"
        with open(result_file, "w") as f:
            json.dump(expected_result, f)
        
        with webserver.test_client() as client:
            response = client.get(f'/api/get_results/{valid_job_id}')
            data = response.get_json()
            self.assertEqual(data.get("status"), "done")
            self.assertEqual(data.get("data"), expected_result)

if __name__ == '__main__':
    unittest.main()
