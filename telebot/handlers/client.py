from aiogram import types, Dispatcher

from bot import bot


async def answer(message: types.Message):
    await bot.send_message(message.from_user.id, 'shut yo bitch ass')


def register_handlers_client(db: Dispatcher):
    db.register_message_handler(answer, content_types=['document'])
