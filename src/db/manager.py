from dotenv import load_dotenv
import os
import pymysql

class DataBaseManager:
    def __init__(self):
        load_dotenv()
        try:
            self.connection = pymysql.connect(host=os.getenv('DB_HOST'),
                                     user=os.getenv('DB_USER'),
                                     password=os.getenv('DB_PASSWORD'),
                                     database=os.getenv('DB_NAME'))
            
            self.cursor = self.connection.cursor()
            print('Connected to db.')
        except pymysql.Error as e:
            print(f'Error connected to db: {e}')
            self.connection = None

    def execute(self, sql, params=None):
        try:
            self.cursor.execute(sql, params)
            return self.cursor
        except pymysql.Error as e:
            print(f'Error execute: {e}')
    
    def executemany(self, sql, params_list):
        try:
            self.cursor.executemany(sql, params_list)
            return self.cursor
        except pymysql.Error as e:
            print(f'Error executemany: {e}')

    def commit(self):
        try:
            self.connection.commit()
        except pymysql.Error as e:
            print(f'Error committing: {e}')
            self.connection.rollback()

    def close(self):
        self.cursor.close()
        self.connection.close()
        print('DB connection closed.')

if __name__ == "__main__":
    db = DataBaseManager()
