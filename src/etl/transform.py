import pandas as pd

class DataTransformer:
    def __init__(self):
        self.market_mapping = {}
        self.action_mapping = {}
        self.buyer_mapping = {}

    def clean_csv(self, df: pd.DataFrame) -> pd.DataFrame:
        # 移除重複的header
        df.drop_duplicates(inplace=True, keep=False)
        df.set_index('Transaction Hash', inplace=True)
        df['DateTime (UTC'] = pd.to_datetime(df['DateTime (UTC)'])
        # 移除用不到的column
        df.drop(['NFT', 'Blockno', 'UnixTimestamp', 'Quantity', 'Type'], axis=1, inplace=True)
        # 移除交易價格為0和沒有買家的資料
        df.dropna(subset=['Price', 'Buyer'], inplace=True)
        df = df[~df['Price'].str.contains('0 ETH|0 WETH')]
        # clean price for USD only
        df.loc[:, 'Price'] = df['Price'].apply(self.__extract_usd).astype(float)
        # 依時間排序
        df = df.sort_values(by='DateTime (UTC)')
        return df

    def __extract_usd(self, value):
        if "(" in value:
            start = value.find('($') + 2 #start after ($
            end = value.find(')')
            return value[start:end].replace(',', '')
        else:
            return ''.join(c for c in value if c.isdigit()).strip()
        
    def extract_unique_markets(self, df):
        unique_markets = df['Market'].drop_duplicates().reset_index(drop=True)
        self.market_mapping = {name: idx + 1 for idx, name in enumerate(unique_markets)}
        return pd.DataFrame(
            list(self.market_mapping.items()), columns=['name', 'id']
        )

    def extract_unique_actions(self, df):
        unique_actions = df['Action'].drop_duplicates().reset_index(drop=True)
        self.action_mapping = {name: idx + 1 for idx, name in enumerate(unique_actions)}
        return pd.DataFrame(
            list(self.action_mapping.items()), columns=['name', 'id']
        )

    def extract_unique_buyers(self, df):
        unique_buyers = df['Buyer'].drop_duplicates().reset_index(drop=True)
        self.buyer_mapping = {name: idx + 1 for idx, name in enumerate(unique_buyers)}
        return pd.DataFrame(
            list(self.buyer_mapping.items()), columns=['address', 'id']
        )

    def normalize_transactions(self, df):
        df['market_id'] = df['Market'].map(self.market_mapping)
        df['action_id'] = df['Action'].map(self.action_mapping)
        df['buyer_id'] = df['Buyer'].map(self.buyer_mapping)
        df.drop(columns=['Market'], inplace=True)
        df.drop(columns=['Action'], inplace=True)
        df.drop(columns=['Buyer'], inplace=True)
        return df

if __name__ == '__main__':
    from extract import Extractor
    transformer = DataTransformer()

    df = Extractor(csv_path='../../python/BAYC_trades/all_time.csv').load_csv()
    cleaned_data = transformer.clean_csv(df=df)
    market_df = transformer.extract_unique_markets(cleaned_data)
    action_df = transformer.extract_unique_actions(cleaned_data)
    address_df = transformer.extract_unique_buyers(cleaned_data)
    print(transformer.normalize_transactions(df=cleaned_data))