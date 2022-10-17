import os

from sqlalchemy import create_engine


username = os.getenv('DB_USERNAME')
password = os.getenv('DB_PASSWORD')
host = os.getenv('HOST') or 'localhost'
port = ':'+os.getenv('DB_PORT') or ''
db = os.getenv('DB_NAME')
engine = create_engine(f'postgresql+psycopg2://{username}:{password}@{host}{port}/{db}')
