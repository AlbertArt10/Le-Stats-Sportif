import unittest
from app import webserver

class TestGracefulShutdown(unittest.TestCase):
    def setUp(self):
        # Înainte de fiecare test, curățăm coada de joburi
        while not webserver.tasks_runner.job_queue.empty():
            try:
                webserver.tasks_runner.job_queue.get_nowait()
            except Exception:
                break
        # Resetarea shutdown_event nu este direct posibilă, dar testele sunt ordonate astfel încât fiecare verificare să fie independentă.
    
    def test_graceful_shutdown_done(self):
        """
        Testăm situația când coada de joburi este goală.
        Așteptăm ca apelul GET la /api/graceful_shutdown să returneze status "done".
        """
        with webserver.test_client() as client:
            response = client.get('/api/graceful_shutdown')
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertEqual(data.get("status"), "done")
    
    def test_graceful_shutdown_running(self):
        """
        Testăm situația când coada de joburi conține cel puțin un job.
        Așteptăm ca apelul GET la /api/graceful_shutdown să returneze status "running".
        """
        # Adăugăm un job dummy pentru a simula o coadă non-goală
        dummy_job = lambda: ({"dummy": True}, "dummy_job")
        webserver.tasks_runner.job_queue.put(dummy_job)
        
        with webserver.test_client() as client:
            response = client.get('/api/graceful_shutdown')
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertEqual(data.get("status"), "running")
        
        # Curățăm coada după test
        while not webserver.tasks_runner.job_queue.empty():
            try:
                webserver.tasks_runner.job_queue.get_nowait()
            except Exception:
                break

if __name__ == '__main__':
    unittest.main()
