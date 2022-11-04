from aiogram.utils import executor

from bot import dp
from entities.db.db_engine import engine
from handlers.admin import register_handlers_admin
from handlers.client import register_handlers_client
from entities.db.db_tables import Base

Base.metadata.create_all(engine)


register_handlers_client(dp)
register_handlers_admin(dp)

executor.start_polling(dp, skip_updates=True)

