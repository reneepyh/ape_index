from src.etl.extract import DataExtractor
from src.etl.transform import DataTransformer
from src.etl.load import DataLoader

class Pipeline:
    def __init__(self):
        self.extractor = DataExtractor(csv_path='../../python/BAYC_trades/all_time.csv')
        self.transformer = DataTransformer()
        self.loader = DataLoader()
    
    def run(self):
        raw_data = self.extractor.load_csv()
        cleaned_data = self.transformer.clean_csv(df=raw_data)

        markets_df = self.transformer.extract_unique_markets(cleaned_data)
        actions_df = self.transformer.extract_unique_actions(cleaned_data)
        addresses_df = self.transformer.extract_unique_buyers(cleaned_data)

        self.loader.insert_markets(markets_df=markets_df)
        self.loader.insert_actions(actions_df=actions_df)
        self.loader.insert_addresses(addresses_df=addresses_df)
        self.loader.insert_transactions(transactions_df=cleaned_data)

        self.loader.close_connection()

