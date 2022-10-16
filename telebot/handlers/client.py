from aiogram import types, Dispatcher

from bot import bot
from tasks import validate


async def answer(message: types.Message):
    await bot.send_message(message.from_user.id, 'working...')
    validate.delay(message.text)
    await message.delete()


def register_handlers_client(db: Dispatcher):
    db.register_message_handler(answer)
