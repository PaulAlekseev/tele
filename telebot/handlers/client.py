import datetime

from aiogram import types, Dispatcher

from bot import bot
from entities.async_db.db_engine import async_session
from entities.async_db.db_repos import AIOCredentialRepo, AIOScanRepo
from entities.async_db.db_specifications import AIOScanDateUserSpecification
from tasks import validate, request


async def answer(message: types.Message):
    await bot.send_message(message.from_user.id, 'working...')
    if len(message.text.split('|')) == 3:
        validate.delay(message.text, message.from_user.id)
    else:
        request.delay()
    await message.delete()


async def db_answer(message: types.Message):
    async with async_session() as session:
        async with session.begin():
            credentials_repo = AIOCredentialRepo(session)
            scan_repo = AIOScanRepo(session)
            scan_result = scan_repo.get_with(AIOScanDateUserSpecification(0, datetime.date.today()))
            await bot.send_message(message.from_user.id, [(item.url, item.login, item.password) for item in (await credentials_repo.get_all_credentials())[0]])
            print(scan_result)


def register_handlers_client(db: Dispatcher):
    db.register_message_handler(db_answer, commands=['start'])
    db.register_message_handler(answer)
