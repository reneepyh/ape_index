from db.manager import DataBaseManager

class DataLoader:
    def __init__(self):
        self.db = DataBaseManager()
    
    def insert_markets(self, markets_df):
        sql = """
        INSERT INTO markets (id, name)
        VALUES (%s, %s)
        """
        try:
            params = list(markets_df[['id', 'name']].itertuples(index=False, name=None))
            self.db.executemany(sql, params)
            self.db.commit()
            print(f'{len(params)} markets inserted successfully.')
        except Exception as e:
            print(f'Error inserting markets: {e}')

    def insert_addresses(self, addresses_df):
        sql = """
        INSERT INTO addresses (id, name)
        VALUES (%s, %s)
        """
        try:
            params = list(addresses_df[['id', 'address']].itertuples(index=False, name=None))
            self.db.executemany(sql, params)
            self.db.commit()
            print(f'{len(params)} actions inserted successfully.')
        except Exception as e:
            print(f'Error inserting addresses: {e}')

    def insert_actions(self, actions_df):
        sql = """
        INSERT INTO actions (id, name)
        VALUES (%s, %s)
        """
        try:
            params = list(actions_df[['id', 'name']].itertuples(index=False, name=None))
            self.db.executemany(sql, params)
            self.db.commit()
            print(f'{len(params)} actions inserted successfully.')
        except Exception as e:
            print(f'Error inserting actions: {e}')

    def insert_transactions(self, transactions_df):
        sql = """
        INSERT INTO transactions (id, time, action_id, buyer_id, token_id, price, market_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        try:
            params = list(transactions_df.itertuples(index=False, name=None))
            self.db.executemany(sql, params)
            self.db.commit()
            print(f'{len(params)} transactions inserted successfully.')
        except Exception as e:
            print(f'Error inserting transactions: {e}')