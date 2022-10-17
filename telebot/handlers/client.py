from aiogram import types, Dispatcher

from bot import bot
from tasks import validate, request


async def answer(message: types.Message):
    await bot.send_message(message.from_user.id, 'working...')
    if len(message.text.split('|')) == 3:
        validate.delay(message.text)
    else:
        request.delay()
    await message.delete()


def register_handlers_client(db: Dispatcher):
    db.register_message_handler(answer)
