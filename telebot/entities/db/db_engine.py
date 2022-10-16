from sqlalchemy import create_engine

from entities.constants import DATABASE_PATH

engine = create_engine(f'sqlite:///{DATABASE_PATH}')
