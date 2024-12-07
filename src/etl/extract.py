import time
import os
import httpx
import pandas as pd
from dotenv import load_dotenv

class Extractor:
    def __init__(self, csv_path):
        load_dotenv()
        self.csv_path = csv_path

    def load_csv(self):
        return pd.read_csv(self.csv_path)
    
    def fetch_token(self, token_id):
        url = f'https://deep-index.moralis.io/api/v2.2/nft/0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D/{token_id}'
        headers = {'X-API-Key': os.getenv('MORALIS_APIKEY')}
        response = httpx.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    
    def fetch_token_in_batches(self, batch_size=100):
        start_id = 1
        end_id = 10000

        for batch_start in range(start_id, end_id + 1, batch_size):
            batch_end = min(batch_start + batch_size - 1, end_id)
            batch_data = []
            for token_id in range(batch_start, batch_end + 1):
                try:
                    batch_data.append(self.fetch_token(token_id))
                except httpx.HTTPError as e:
                    print(f'Failed to fetch token ID {token_id}: {e}')
                    continue
                time.sleep(0.2)
            yield batch_data

if __name__ == "__main__":
    batch_data_list = Extractor(csv_path='..').fetch_token_in_batches(batch_size=10)
    try:
        for batch_data in batch_data_list:
            print(f'Fetched batch: {batch_data}')
            break
    except Exception as e:
        print(f'Error occurred: {e}')