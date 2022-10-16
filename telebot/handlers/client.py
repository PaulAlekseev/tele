from aiogram import types, Dispatcher

from bot import bot
from handlers.tasks import add


async def answer(message: types.Message):
    await bot.send_message(message.from_user.id, 'shut yo bitch ass')
    await bot.send_message(message.from_user.id, 'You should end your live NOW')
    add.delay(1, 2)
    await message.delete()


def register_handlers_client(db: Dispatcher):
    db.register_message_handler(answer)
