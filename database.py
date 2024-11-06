import psycopg2
from config import Config

password = Config.password

class Database():
    def __init__(self) -> None:
        try:
            self.db = psycopg2.connect(host='127.0.0.1',dbname='postgres',user='postgres',password=password,port=5432)
            self.cursor = self.db.cursor()
        except Exception as e:
            print(f'database connection err {e}')
            raise
        
    def __del__(self):
        try:
            if hasattr(self, 'cursor') and self.cursor:
                self.cursor.close()
            if hasattr(self, 'db') and self.db:
                self.db.close()
        except Exception as e:
            print(f'closing database err {e}')

    def execute(self,query,args={}):
        self.cursor.execute(query,args)
        row = self.cursor.fetchall()
        return row

    def commit(self):
        self.cursor.commit()