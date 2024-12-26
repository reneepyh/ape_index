import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime
from src.playwright.crawler import Crawler
from src.etl.db.manager import DataBaseManager
from src.etl.extract import DataExtractor
from src.etl.transform import DataTransformer
from src.etl.load import DataLoader

class Pipeline:
    def __init__(self):
        load_dotenv()
        
        self.db = DataBaseManager()
        self.crawler = Crawler(base_url=os.getenv('CRAW_PAGE'))
        self.extractor = DataExtractor()
        self.transformer = DataTransformer(db=self.db)
        self.loader = DataLoader(db=self.db)
    
    def run(self):
        # # 取得最後一筆資料的時間
        # latest = self.db.fetch_one("SELECT time FROM transactions ORDER BY time DESC LIMIT 1")
        # last_known_time = latest[0] if latest else None
        # self.crawler.crawl_all_pages(last_known_time=last_known_time)
        # current_time = datetime.now().strftime("%Y%m%d_%H%M%S")

        # folder_path = Path("src/etl/db/raw")
        # folder_path.mkdir(parents=True, exist_ok=True)
        # file_path = folder_path / f'transactions_{current_time}.csv'
        # saved_file = self.crawler.save_to_csv(file_path)

        # if not saved_file:
        #     print("No new data crawled. Exit pipeline.")
        #     self.loader.close_connection()
        #     return
        
        raw_data = self.extractor.load_csv(csv_path="src/etl/db/raw/transactions_20241225_230007.csv")
        cleaned_data = self.transformer.clean_csv(df=raw_data)

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
