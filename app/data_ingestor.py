import os
import json
import pandas as pd

class DataIngestor:
    def __init__(self, csv_path: str):
        # Citirea CSV-ului folosind pandas
        self.df = pd.read_csv(csv_path)

        # Convertim coloana Data_Value la numeric
        self.df['Data_Value'] = pd.to_numeric(self.df['Data_Value'], errors='coerce')
        print("CSV loaded successfully. Number of rows:", len(self.df))

        self.questions_best_is_min = [
            'Percent of adults aged 18 years and older who have an overweight classification',
            'Percent of adults aged 18 years and older who have obesity',
            'Percent of adults who engage in no leisure-time physical activity',
            'Percent of adults who report consuming fruit less than one time daily',
            'Percent of adults who report consuming vegetables less than one time daily'
        ]

        self.questions_best_is_max = [
            'Percent of adults who achieve at least 150 minutes a week of moderate-intensity aerobic physical activity or 75 minutes a week of vigorous-intensity aerobic activity (or an equivalent combination)',
            'Percent of adults who achieve at least 150 minutes a week of moderate-intensity aerobic physical activity or 75 minutes a week of vigorous-intensity aerobic physical activity and engage in muscle-strengthening activities on 2 or more days a week',
            'Percent of adults who achieve at least 300 minutes a week of moderate-intensity aerobic physical activity or 150 minutes a week of vigorous-intensity aerobic activity (or an equivalent combination)',
            'Percent of adults who engage in muscle-strengthening activities on 2 or more days a week',
        ]

    def compute_states_mean(self, question: str) -> dict:
        # Filtrăm datele pentru întrebarea primită
        df_filtered = self.df[self.df['Question'] == question]
        # Grupăm după "LocationAbbr" și calculăm media valorilor din "Data_Value"
        means = df_filtered.groupby('LocationAbbr')['Data_Value'].mean().to_dict()
        return means
