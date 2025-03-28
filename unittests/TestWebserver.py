import unittest
import time
import os
import json
from app import webserver

class TestWebserver(unittest.TestCase):

    def setUp(self):
        # Resetăm contorul și dicționarul de joburi
        webserver.job_counter = 1
        webserver.job_status.clear()
        # Curățăm coada de joburi
        while not webserver.tasks_runner.job_queue.empty():
            try:
                webserver.tasks_runner.job_queue.get_nowait()
                webserver.tasks_runner.job_queue.task_done()
            except Exception:
                break

    def tearDown(self):
        # Ștergem toate fișierele din directorul "results" pentru a evita reziduurile
        results_dir = "results"
        for filename in os.listdir(results_dir):
            file_path = os.path.join(results_dir, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                webserver.logger.warning("Nu am putut șterge fișierul %s: %s", file_path, e)

    def poll_result(self, job_id, timeout=10, poll_interval=0.2):
        """Așteaptă până când jobul identificat prin job_id are status 'done'
        sau până la expirarea timeout-ului."""
        client = webserver.test_client()
        start_time = time.time()
        result_data = None
        while time.time() - start_time < timeout:
            response = client.get(f"/api/get_results/{job_id}")
            try:
                result_data = response.get_json()
            except Exception as e:
                # Dacă fișierul nu este un JSON valid, încercăm din nou
                time.sleep(poll_interval)
                continue
            if result_data is not None and result_data.get("status") == "done":
                return result_data
            time.sleep(poll_interval)
        return result_data

    def test_post_endpoint(self):
        client = webserver.test_client()
        payload = {"message": "hello"}
        response = client.post("/api/post_endpoint", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("message", data)
        self.assertEqual(data["message"], "Received data successfully")
        self.assertEqual(data["data"], payload)

    def test_states_mean(self):
        client = webserver.test_client()
        payload = {"question": "Percent of adults who engage in no leisure-time physical activity"}
        response = client.post("/api/states_mean", json=payload)
        self.assertEqual(response.status_code, 200)
        job_id = response.get_json().get("job_id")
        self.assertTrue(job_id.startswith("job_id_"))
        result_data = self.poll_result(job_id)
        self.assertIsNotNone(result_data, "Timeout: Nu s-a obținut niciun răspuns")
        self.assertEqual(result_data.get("status"), "done")
        data = result_data.get("data")
        self.assertIsInstance(data, dict)
        self.assertGreater(len(data), 0)

    def test_state_mean(self):
        client = webserver.test_client()
        payload = {
            "question": "Percent of adults who engage in no leisure-time physical activity",
            "state": "California"
        }
        response = client.post("/api/state_mean", json=payload)
        self.assertEqual(response.status_code, 200)
        job_id = response.get_json().get("job_id")
        result_data = self.poll_result(job_id)
        self.assertIsNotNone(result_data, "Timeout: Nu s-a obținut niciun răspuns")
        self.assertEqual(result_data.get("status"), "done")
        data = result_data.get("data")
        self.assertIsInstance(data, dict)
        self.assertIn("California", data)

    def test_best5(self):
        client = webserver.test_client()
        payload = {
            "question": "Percent of adults aged 18 years and older who have obesity"
        }
        response = client.post("/api/best5", json=payload)
        self.assertEqual(response.status_code, 200)
        job_id = response.get_json().get("job_id")
        result_data = self.poll_result(job_id)
        self.assertIsNotNone(result_data, "Timeout: Nu s-a obținut niciun răspuns")
        self.assertEqual(result_data.get("status"), "done")
        data = result_data.get("data")
        self.assertIsInstance(data, dict)
        # Verificăm că am primit cel mult 5 rezultate și cel puțin 1
        self.assertLessEqual(len(data), 5)
        self.assertGreater(len(data), 0)

    def test_worst5(self):
        client = webserver.test_client()
        payload = {
            "question": "Percent of adults who engage in muscle-strengthening activities on 2 or more days a week"
        }
        response = client.post("/api/worst5", json=payload)
        self.assertEqual(response.status_code, 200)
        job_id = response.get_json().get("job_id")
        result_data = self.poll_result(job_id)
        self.assertIsNotNone(result_data, "Timeout: Nu s-a obținut niciun răspuns")
        self.assertEqual(result_data.get("status"), "done")
        data = result_data.get("data")
        self.assertIsInstance(data, dict)
        total_states = len(webserver.data_ingestor.compute_states_mean(payload["question"]))
        expected = 5 if total_states >= 5 else total_states
        self.assertEqual(len(data), expected)

    def test_global_mean(self):
        client = webserver.test_client()
        payload = {"question": "Percent of adults who engage in no leisure-time physical activity"}
        response = client.post("/api/global_mean", json=payload)
        self.assertEqual(response.status_code, 200)
        job_id = response.get_json().get("job_id")
        result_data = self.poll_result(job_id, timeout=10)
        self.assertIsNotNone(result_data, "Timeout: Nu s-a obținut niciun răspuns")
        self.assertEqual(result_data.get("status"), "done")
        data = result_data.get("data")
        # Acceptă fie un dicționar cu cheia "global_mean", fie o valoare numerică directă.
        if isinstance(data, dict):
            self.assertIn("global_mean", data, "Cheia 'global_mean' lipsește în rezultat")
            self.assertIsInstance(data["global_mean"], (float, int))
        else:
            self.assertIsInstance(data, (float, int))

    def test_diff_from_mean(self):
        client = webserver.test_client()
        payload = {"question": "Percent of adults who engage in no leisure-time physical activity"}
        response = client.post("/api/diff_from_mean", json=payload)
        self.assertEqual(response.status_code, 200)
        job_id = response.get_json().get("job_id")
        result_data = self.poll_result(job_id, timeout=10)
        self.assertIsNotNone(result_data, "Timeout: Nu s-a obținut niciun răspuns")
        self.assertEqual(result_data.get("status"), "done")
        data = result_data.get("data")
        self.assertIsInstance(data, dict)
        self.assertGreater(len(data), 0)

    def test_state_diff_from_mean(self):
        client = webserver.test_client()
        payload = {
            "question": "Percent of adults who engage in no leisure-time physical activity",
            "state": "California"
        }
        response = client.post("/api/state_diff_from_mean", json=payload)
        self.assertEqual(response.status_code, 200)
        job_id = response.get_json().get("job_id")
        result_data = self.poll_result(job_id, timeout=10)
        self.assertIsNotNone(result_data, "Timeout: Nu s-a obținut niciun răspuns")
        self.assertEqual(result_data.get("status"), "done")
        data = result_data.get("data")
        self.assertIsInstance(data, dict)
        self.assertIn("California", data)

    def test_mean_by_category(self):
        client = webserver.test_client()
        payload = {"question": "Percent of adults who engage in no leisure-time physical activity"}
        response = client.post("/api/mean_by_category", json=payload)
        self.assertEqual(response.status_code, 200)
        job_id = response.get_json().get("job_id")
        result_data = self.poll_result(job_id, timeout=10)
        self.assertIsNotNone(result_data, "Timeout: Nu s-a obținut niciun răspuns")
        self.assertEqual(result_data.get("status"), "done")
        data = result_data.get("data")
        self.assertIsInstance(data, dict)
        self.assertGreater(len(data), 0)

    def test_state_mean_by_category(self):
        client = webserver.test_client()
        payload = {
            "question": "Percent of adults who engage in no leisure-time physical activity",
            "state": "California"
        }
        response = client.post("/api/state_mean_by_category", json=payload)
        self.assertEqual(response.status_code, 200)
        job_id = response.get_json().get("job_id")
        result_data = self.poll_result(job_id, timeout=10)
        self.assertIsNotNone(result_data, "Timeout: Nu s-a obținut niciun răspuns")
        self.assertEqual(result_data.get("status"), "done")
        data = result_data.get("data")
        self.assertIsInstance(data, dict)
        self.assertIn("California", data)

    def test_graceful_shutdown(self):
        client = webserver.test_client()
        # Asigurăm că coada este goală
        while not webserver.tasks_runner.job_queue.empty():
            try:
                webserver.tasks_runner.job_queue.get_nowait()
                webserver.tasks_runner.job_queue.task_done()
            except Exception:
                break
        response = client.get("/api/graceful_shutdown")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data.get("status"), "done")

    def test_jobs_endpoint(self):
        client = webserver.test_client()
        # Pre-populăm job_status pentru test
        webserver.job_status.update({
            "job_id_1": "done",
            "job_id_2": "running",
            "job_id_3": "running"
        })
        response = client.get("/api/jobs")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data.get("status"), "done")
        self.assertEqual(data.get("data"), webserver.job_status)

    def test_num_jobs_endpoint(self):
        client = webserver.test_client()
        # Adăugăm câteva joburi dummy în coadă
        def dummy_job():
            return {"dummy": True}, "dummy_job"
        for _ in range(3):
            webserver.tasks_runner.job_queue.put(dummy_job)
        response = client.get("/api/num_jobs")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data.get("num_jobs"), 3)
        # Curățăm coada după test
        while not webserver.tasks_runner.job_queue.empty():
            try:
                webserver.tasks_runner.job_queue.get_nowait()
                webserver.tasks_runner.job_queue.task_done()
            except Exception:
                break

if __name__ == '__main__':
    unittest.main()
