import pandas as pd

class DataTransformer:
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
        df['Price'] = df['Price'].apply(self.__extract_usd).astype(float)
        # 依時間排序
        df.sort_values(by='DateTime (UTC)', inplace= True)
        return df

    def __extract_usd(self, value):
        if "(" in value:
            start = value.find('($') + 2 #start after ($
            end = value.find(')')
            return value[start:end].replace(',', '')
        else:
            return ''.join(c for c in value if c.isdigit()).strip()

if __name__ == '__main__':
    from extract import Extractor

    df = Extractor(csv_path='../../python/BAYC_trades/all_time.csv').load_csv()
    print(DataTransformer().clean_csv(df=df))