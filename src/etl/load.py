class DataLoader:
    def __init__(self, db):
        self.db = db
    
    def insert_markets(self, markets_df):
        try:
            sql = """
            INSERT IGNORE INTO markets (name)
            VALUES (%s)
            """
            
            params = list(markets_df.drop_duplicates().itertuples(index=False, name=None))
            self.db.executemany(sql, params)
            self.db.commit()
            print(f'{len(params)} markets inserted successfully.')
        except Exception as e:
            print(f'Error inserting markets: {e}')

    def insert_addresses(self, addresses_df):
        try:
            sql = """
            INSERT IGNORE INTO addresses (address)
            VALUES (%s)
            """
  
            params = list(addresses_df.drop_duplicates().itertuples(index=False, name=None))
            self.db.executemany(sql, params)
            self.db.commit()
            print(f'{len(params)} addresss inserted successfully.')
        except Exception as e:
            print(f'Error inserting addresss: {e}')

    def insert_actions(self, actions_df):
        try:
            sql = """
            INSERT IGNORE INTO actions (name)
            VALUES (%s)
            """

            params = list(actions_df.drop_duplicates().itertuples(index=False, name=None))
            self.db.executemany(sql, params)
            self.db.commit()
            print(f'{len(params)} actions inserted successfully.')
        except Exception as e:
            print(f'Error inserting actions: {e}')

    def insert_transactions(self, transactions_df):
        try:
            sql = """
            INSERT INTO transactions (transaction_hash, time, price, token_id, market_id, action_id, buyer_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            params = list(transactions_df.itertuples(index=False, name=None))
            self.db.executemany(sql, params)
            self.db.commit()
            print(f'{len(params)} transactions inserted successfully.')
        except Exception as e:
            print(f'Error inserting transactions: {e}')

    def close_connection(self):
        self.db.close()