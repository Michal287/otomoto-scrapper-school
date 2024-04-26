from sqlalchemy import create_engine

class OtomotoDB:
    def __init__(self):
        self.engine = None

    def connect(self, hostname, database_name, username, password, port):
        self.engine = create_engine(f"postgresql://{username}:{password}@{hostname}:{port}/{database_name}")
    
    def send_data(self, df):
        try:
            df.to_sql('posts_testing', con=self.engine, index=False, if_exists='replace')

        except Exception:
            print("Failed to connect to the server.")