import os
from pathlib import Path
from dotenv import load_dotenv
from src.playwright.crawler import Crawler
from src.db.manager import DataBaseManager
from src.etl.extract import DataExtractor
from src.etl.transform import DataTransformer
from src.etl.load import DataLoader

class Pipeline:
    def __init__(self):
        load_dotenv()
        base_dir = Path(__file__).resolve().parent.parent
        
        self.db = DataBaseManager()
        self.crawler = Crawler(base_url=os.getenv('CRAW_PAGE'))
        self.extractor = DataExtractor(csv_path=base_dir / 'db/raw/transactions.csv')
        self.transformer = DataTransformer(db=self.db)
        self.loader = DataLoader(db=self.db)
    
    def run(self):
        #self.crawler.crawl_all_pages()
        #self.crawler.save_to_csv('transactions.csv')
        raw_data = self.extractor.load_csv()
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
