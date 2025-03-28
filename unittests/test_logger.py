import unittest
import os
import time

class TestLoggerFunctionality(unittest.TestCase):
    def setUp(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.join(base_dir, "..")
        self.log_file = os.path.join(project_root, "webserver.log")

        if os.path.exists(self.log_file):
            os.remove(self.log_file)

        # Importăm webserver-ul abia acum, după ce am curățat logul
        from app import webserver
        from app.logger_setup import setup_logger
        self.webserver = webserver
        self.webserver.logger = setup_logger()
        self.webserver.logger.info("Logger configurat în test.")

    def tearDown(self):
        # Închidem handler-ele după fiecare test
        for handler in self.webserver.logger.handlers:
            handler.close()

    def read_log(self):
        timeout = 5
        start_time = time.time()
        while not os.path.exists(self.log_file) and (time.time() - start_time < timeout):
            time.sleep(0.1)
        if not os.path.exists(self.log_file):
            self.fail(f"Log file '{self.log_file}' not found after waiting {timeout} seconds.")
        with open(self.log_file, "r") as f:
            return f.read()

    def test_post_endpoint_logging(self):
        client = self.webserver.test_client()
        response = client.post("/api/post_endpoint", json={"message": "test log"})
        self.assertEqual(response.status_code, 200)
        for handler in self.webserver.logger.handlers:
            handler.flush()
        time.sleep(0.5)
        log_contents = self.read_log()
        self.assertIn("Intrare în /api/post_endpoint", log_contents)
        self.assertIn("Iesire din /api/post_endpoint", log_contents)

    def test_states_mean_logging(self):
        client = self.webserver.test_client()
        payload = {"question": "Percent of adults who engage in no leisure-time physical activity"}
        response = client.post("/api/states_mean", json=payload)
        self.assertEqual(response.status_code, 200)
        for handler in self.webserver.logger.handlers:
            handler.flush()
        time.sleep(0.5)
        log_contents = self.read_log()
        self.assertIn("Intrare în /api/states_mean", log_contents)
        self.assertIn("Job-ul", log_contents)

    def test_global_mean_logging(self):
        client = self.webserver.test_client()
        payload = {"question": "Percent of adults who engage in no leisure-time physical activity"}
        response = client.post("/api/global_mean", json=payload)
        self.assertEqual(response.status_code, 200)
        for handler in self.webserver.logger.handlers:
            handler.flush()
        log_contents = self.read_log()
        self.assertIn("Intrare în /api/global_mean", log_contents)
        self.assertIn("Job-ul", log_contents)

if __name__ == '__main__':
    unittest.main()
