import pandas as pd

class DataExtractor:
    def load_csv(self, csv_path):
        return pd.read_csv(csv_path)
