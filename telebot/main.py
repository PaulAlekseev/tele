from aiogram.utils import executor

from bot import db
from entities.db.db_engine import engine

from handlers.client import register_handlers_client
from entities.db.db_tables import Base

Base.metadata.create_all(engine)


register_handlers_client(db)

executor.start_polling(db, skip_updates=True)

