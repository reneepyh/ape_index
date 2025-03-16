import os
import pandas as pd
import boto3
from io import StringIO
from dotenv import load_dotenv

class DataTransformer:
    def __init__(self, db):
        load_dotenv()
        self.db = db
        self.s3_client = boto3.client('s3')
        self.market_mapping = {}
        self.action_mapping = {}
        self.buyer_mapping = {}

    def clean_csv(self, df: pd.DataFrame) -> pd.DataFrame:
        df['DateTime (UTC)'] = pd.to_datetime(df['DateTime (UTC)'])
        
        # 移除交易價格為0, EDC幣別,和沒有買家的資料
        df.dropna(subset=['Price', 'Buyer'], inplace=True)
        df = df[~df['Price'].str.contains('0 ETH|0 WETH|EDC')]
        # clean price for USD only
        df.loc[:, 'Price'] = df['Price'].apply(self.__extract_usd).astype(float, errors='ignore')
        df = df.dropna(subset=['Price'])
        # 依時間排序
        df = df.sort_values(by='DateTime (UTC)')
        return df

    def __extract_usd(self, value):
        if "(" in value and "$" in value:
            start = value.find('($') + 2  # Start after ($
            end = value.find(')')
            return value[start:end].replace(',', '')
        elif "USDC" in value or "USD" in value:
            return ''.join(c for c in value if c.isdigit() or c == '.').strip()
        else:
            return None

        
    def extract_unique_markets(self, df):
        unique_markets = df['Market'].drop_duplicates().reset_index(drop=True)
        return unique_markets.to_frame(name='name')

    def extract_unique_actions(self, df):
        unique_actions = df['Action'].drop_duplicates().reset_index(drop=True)
        return unique_actions.to_frame(name='name')

    def extract_unique_buyers(self, df):
        unique_buyers = df['Buyer'].drop_duplicates().reset_index(drop=True)
        return unique_buyers.to_frame(name='address')
    
    def create_markets_mapping(self):
        try:
            sql = "SELECT id, name FROM markets"
            rows = self.db.fetch_all(sql)

            markets_df = pd.DataFrame(rows, columns=['id', 'name'])
            print("Market Mapping Retrieved Successfully:")
            print(markets_df.head())

            self.market_mapping = dict(zip(markets_df['name'], markets_df['id']))
        except Exception as e:
            print(f"Error retrieving action mapping: {e}")
    
    def create_action_mapping(self):
        try:
            sql = "SELECT id, name FROM actions"
            rows = self.db.fetch_all(sql)
            print(rows)
            actions_df = pd.DataFrame(rows, columns=['id', 'name'])
            print("Action Mapping Retrieved Successfully:")
            print(actions_df.head())

            self.action_mapping = dict(zip(actions_df['name'], actions_df['id']))
        except Exception as e:
            print(f"Error retrieving action mapping: {e}")

    def create_buyers_mapping(self):
        try:
            sql = "SELECT id, address FROM addresses"
            rows = self.db.fetch_all(sql)

            buyers_df = pd.DataFrame(rows, columns=['id', 'address'])
            print("Buyer Mapping Retrieved Successfully:")
            print(buyers_df.head())

            self.buyer_mapping = dict(zip(buyers_df['address'], buyers_df['id']))
        except Exception as e:
            print(f"Error retrieving buyer mapping: {e}")

    def normalize_transactions(self, df):
        df['market_id'] = df['Market'].map(self.market_mapping)
        df['action_id'] = df['Action'].map(self.action_mapping)
        df['buyer_id'] = df['Buyer'].map(self.buyer_mapping)
        df.drop(columns=['Market'], inplace=True)
        df.drop(columns=['Action'], inplace=True)
        df.drop(columns=['Buyer'], inplace=True)
        return df
    
    def load_from_s3(self, key):
        try:
            response = self.s3_client.get_object(Bucket=os.getenv('BUCKET_NAME'), Key=key)
            csv_data = response['Body'].read().decode('utf-8')
            return pd.read_csv(StringIO(csv_data))
        except Exception as e:
            print(f"Error loading file from S3: {e}")
            raise
    
    def save_cleaned_to_s3(self, key, df):
        try:
            csv_buffer = StringIO()
            df.to_csv(csv_buffer, index=False)
            self.s3_client.put_object(Bucket=os.getenv('BUCKET_NAME'), Key=key, Body=csv_buffer.getvalue())
            print(f"File successfully saved to s3://{os.getenv('BUCKET_NAME')}/{key}")
        except Exception as e:
            print(f"Error saving file to S3: {e}")
            raise