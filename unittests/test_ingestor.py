import unittest
from app import webserver

class TestDataIngestor(unittest.TestCase):
    def test_dataframe_loaded(self):
        ingestor = webserver.data_ingestor
        df = ingestor.df
        # Verificăm că DataFrame-ul nu este gol
        self.assertIsNotNone(df, "DataFrame-ul este None")
        self.assertGreater(len(df), 0, "DataFrame-ul este gol")
        # Verificăm existența coloanelor esențiale
        expected_columns = ['Data_Value', 'YearStart', 'YearEnd', 'Question', 'LocationDesc']
        for col in expected_columns:
            self.assertIn(col, df.columns, f"Coloana {col} lipsește din DataFrame")
        # Verificăm că putem obține cel puțin 5 rânduri (sau toate, dacă mai puține)
        head = df.head()
        self.assertGreaterEqual(len(head), min(5, len(df)), "Nu s-au obținut cel puțin 5 rânduri din DataFrame")

if __name__ == '__main__':
    unittest.main()
