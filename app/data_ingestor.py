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
        # filtrează datele
        df_filtered = self.df[
            (self.df['YearStart'] >= 2011) &
            (self.df['YearEnd'] <= 2022) &
            (self.df['Question'] == question)
        ]
        # calculează media pentru fiecare stat
        means = df_filtered.groupby('LocationDesc')['Data_Value'].mean()

        # sortează mediile crescător
        means = means.sort_values(ascending=True)

        # returnează rezultatul
        return means.to_dict()


    def compute_state_mean(self, question: str, state: str) -> dict:
        # filtrează datele
        df_filtered = self.df[
            (self.df['YearStart'] >= 2011) &
            (self.df['YearEnd'] <= 2022) &
            (self.df['Question'] == question) &
            (self.df['LocationDesc'] == state)
        ]
        # calculează media pentru statul specificat
        mean_value = df_filtered['Data_Value'].mean()

        # returnează rezultatul
        return {state: mean_value}


    def compute_best5(self, question: str) -> dict:
        # Obținem mediile pe state pentru întrebarea dată
        means = self.compute_states_mean(question)
    
        # Verificăm dacă "best" înseamnă valori minime sau maxime
        if question in self.questions_best_is_min:
            # Cele mai bune sunt cele cu valori mai mici
            sorted_means = sorted(means.items(), key=lambda x: x[1])
        elif question in self.questions_best_is_max:
            # Cele mai bune sunt cele cu valori mai mari
            sorted_means = sorted(means.items(), key=lambda x: x[1], reverse=True)
        else:
            # Dacă nu se recunoaște întrebarea, sortăm crescător ca fallback
            sorted_means = sorted(means.items(), key=lambda x: x[1])
    
        # Selectăm primele 5 state
        best5 = dict(sorted_means[:5])
        return best5


    def compute_worst5(self, question: str) -> dict:
        # Obținem mediile pe state pentru întrebarea dată
        means = self.compute_states_mean(question)
    
        # Pentru întrebările din lista best_is_min, cele mai rele sunt cele cu cele mai mari medii.
        if question in self.questions_best_is_min:
            sorted_means = sorted(means.items(), key=lambda x: x[1], reverse=True)
        # Pentru întrebările din lista best_is_max, cele mai rele sunt cele cu cele mai mici medii.
        elif question in self.questions_best_is_max:
            sorted_means = sorted(means.items(), key=lambda x: x[1])
        else:
            # Fallback: sortează descrescător
            sorted_means = sorted(means.items(), key=lambda x: x[1], reverse=True)
    
        # Selectăm primele 5 state din lista sortată
        worst5 = dict(sorted_means[:5])
        return worst5


    def compute_global_mean(self, question: str) -> dict:
        # Filtrăm datele pentru întrebarea primită
        df_filtered = self.df[
            (self.df['YearStart'] >= 2011) &
            (self.df['YearEnd'] <= 2022) &
            (self.df['Question'] == question)
        ]
        # Calculăm media globală a valorilor din "Data_Value"
        global_mean = df_filtered['Data_Value'].mean()
        # Returnăm rezultatul
        return {"global_mean": global_mean}
