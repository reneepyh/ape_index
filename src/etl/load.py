from db.manager import DataBaseManager

class DataLoader:
    def __init__(self):
        self.db = DataBaseManager()
    
    def insert_markets(self, markets_df):
        try:
            delete_sql = "DELETE FROM markets"
            self.db.execute(delete_sql)
            self.db.commit()

            sql = """
            INSERT INTO markets (id, name)
            VALUES (%s, %s)
            """

            params = list(markets_df[['id', 'name']].itertuples(index=False, name=None))
            self.db.executemany(sql, params)
            self.db.commit()
            print(f'{len(params)} markets inserted successfully.')
        except Exception as e:
            print(f'Error inserting markets: {e}')

    def insert_addresses(self, addresses_df):
        sql = """
        INSERT INTO addresses (id, address)
        VALUES (%s, %s)
        """
        try:
            params = list(addresses_df[['id', 'address']].itertuples(index=False, name=None))
            self.db.executemany(sql, params)
            self.db.commit()
            print(f'{len(params)} addresses inserted successfully.')
        except Exception as e:
            print(f'Error inserting addresses: {e}')

    def insert_actions(self, actions_df):
        try:
            delete_sql = "DELETE FROM actions"
            self.db.execute(delete_sql)
            self.db.commit()

            sql = """
            INSERT INTO actions (id, name)
            VALUES (%s, %s)
            """

            params = list(actions_df[['id', 'name']].itertuples(index=False, name=None))
            self.db.executemany(sql, params)
            self.db.commit()
            print(f'{len(params)} actions inserted successfully.')
        except Exception as e:
            print(f'Error inserting actions: {e}')

    def insert_transactions(self, transactions_df):
        try:
            delete_sql = "DELETE FROM transactions"
            self.db.execute(delete_sql)
            self.db.commit()

            sql = """
            INSERT INTO transactions (id, time, action_id, buyer_id, token_id, price, market_id)
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