from aiogram import types, Dispatcher

from bot import bot
from entities.async_db.db_engine import async_session
from entities.async_db.db_repos import AIOCredentialRepo
from tasks import validate, request


async def answer(message: types.Message):
    await bot.send_message(message.from_user.id, 'working...')
    if len(message.text.split('|')) == 3:
        validate.delay(message.text)
    else:
        request.delay()
    await message.delete()


async def db_answer(message: types.Message):
    await bot.send_message(message.from_user.id, 'bruh')
    async with async_session() as session:
        async with session.begin():
            credentials_repo = AIOCredentialRepo(session)
            await bot.send_message(message.from_user.id, [ item.url for item in await credentials_repo.get_all_credentials()])


def register_handlers_client(db: Dispatcher):
    db.register_message_handler(db_answer, commands=['start'])
    db.register_message_handler(answer)
