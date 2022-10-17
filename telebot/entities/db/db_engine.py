import os

from sqlalchemy import create_engine


engine_string = os.getenv('DB_STRING')
engine = create_engine(engine_string)
