import unittest
from app import webserver

class TestComputeStatesMean(unittest.TestCase):
    def test_states_mean(self):
        ingestor = webserver.data_ingestor
        question = "Percent of adults who engage in no leisure-time physical activity"
        means = ingestor.compute_states_mean(question)
        # Verificăm că se returnează un dicționar
        self.assertIsInstance(means, dict, "Rezultatul trebuie să fie un dicționar")
        # Verificăm că avem cel puțin o intrare
        self.assertGreater(len(means), 0, "Nu s-au calculat medii pentru niciun stat")
        # Verificăm că fiecare medie este un număr (float) și este pozitivă (sau zero)
        for state, mean in means.items():
            self.assertIsInstance(mean, float, f"Media pentru {state} trebuie să fie float")
            self.assertGreaterEqual(mean, 0.0, f"Media pentru {state} este negativă")

if __name__ == '__main__':
    unittest.main()
