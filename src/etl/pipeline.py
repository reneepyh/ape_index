import os
from dotenv import load_dotenv
from datetime import datetime
from db.manager import DataBaseManager
from extract import DataExtractor
from transform import DataTransformer
from load import DataLoader

class Pipeline:
    def __init__(self):
        load_dotenv()
        
        self.db = DataBaseManager()
        self.crawler = DataExtractor(base_url=os.getenv('CRAW_PAGE'))
        self.transformer = DataTransformer(db=self.db)
        self.loader = DataLoader(db=self.db)
    
    def run(self):
        # 取得最後一筆資料的時間
        latest = self.db.fetch_one("SELECT time FROM transactions ORDER BY time DESC LIMIT 1")
        last_known_time = latest[0] if latest else None
        self.crawler.crawl_all_pages(last_known_time=last_known_time)
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        raw_key = f"raw-data/transactions_{current_time}.csv"
        new_data_saved = self.crawler.save_raw_to_s3(key=raw_key)

        if not new_data_saved:
            print("No new data crawled. Exit pipeline.")
            self.loader.close_connection()
            return
        
        raw_data = self.transformer.load_from_s3(key=raw_key)
        cleaned_data = self.transformer.clean_csv(df=raw_data)
        cleaned_key = f"cleaned-data/transactions_cleaned_{current_time}.csv"
        self.transformer.save_cleaned_to_s3(key=cleaned_key, df=cleaned_data)

        self._load_to_rds(cleaned_data)

    def _load_to_rds(self, cleaned_data):
        markets_df = self.transformer.extract_unique_markets(cleaned_data)
        self.loader.insert_markets(markets_df=markets_df)
        self.transformer.create_markets_mapping()

        actions_df = self.transformer.extract_unique_actions(cleaned_data)
        self.loader.insert_actions(actions_df=actions_df)
        self.transformer.create_action_mapping()

        addresses_df = self.transformer.extract_unique_buyers(cleaned_data)
        self.loader.insert_addresses(addresses_df=addresses_df)
        self.transformer.create_buyers_mapping()

        normalize_transactions = self.transformer.normalize_transactions(df=cleaned_data)
        self.loader.insert_transactions(transactions_df=normalize_transactions)

        self.loader.close_connection()
