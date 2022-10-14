from aiogram.utils import executor

from bot import db

from handlers.client import register_handlers_client


register_handlers_client(db)

executor.start_polling(db, skip_updates=True)

