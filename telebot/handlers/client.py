from aiogram import types, Dispatcher

from bot import bot
from celery_tasks.tasks import add


async def answer(message: types.Message):
    await bot.send_message(message.from_user.id, 'shut yo bitch ass')
    await bot.send_message(message.from_user.id, 'You should end your live NOW')
    add.delay()
    await message.delete()


def register_handlers_client(db: Dispatcher):
    db.register_message_handler(answer)
