import pandas as pd

class DataExtractor:
    def __init__(self, csv_path):
        self.csv_path = csv_path

    def load_csv(self):
        return pd.read_csv(self.csv_path)
