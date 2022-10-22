import datetime

from aiogram import types, Dispatcher

from bot import bot
from entities.async_db.db_engine import async_session
from entities.async_db.db_repos import AIOCredentialRepo, AIOScanRepo, AIOUserRepository
from entities.async_db.db_specifications import AIOScanDateUserSpecification, AIOUserTeleIdSpecification
from tasks import validate, request


async def answer(message: types.Message):
    await bot.send_message(message.from_user.id, 'working...')
    if len(message.text.split('|')) == 3:
        async with async_session() as session:
            async with session.begin():
                user_repo = AIOUserRepository(session)
                user = await user_repo.create(message.from_user.id)
        validate.delay(message.text, user.id)
    else:
        request.delay()


async def db_answer(message: types.Message):
    async with async_session() as session:
        async with session.begin():
            credentials_repo = AIOCredentialRepo(session)
            scan_repo = AIOScanRepo(session)
            scan_result = await scan_repo.get_with(AIOScanDateUserSpecification(1, datetime.date.today()))
            await bot.send_message(message.from_user.id, [(item.url, item.login, item.password) for item in
                                                          (await credentials_repo.get_all_credentials())[0]])
            await bot.send_message(message.from_user.id, scan_result)


async def get_user(message: types.Message):
    async with async_session() as session:
        async with session.begin():
            user_repo = AIOUserRepository(session)
            user = await user_repo.get(user_specification=AIOUserTeleIdSpecification(message.from_user.id))
            await bot.send_message(message.from_user.id, user.id)


async def create_user(message: types.Message):
    async with async_session() as session:
        async with session.begin():
            user_repo = AIOUserRepository(session)
            user = await user_repo.create(message.from_user.id)
            await bot.send_message(message.from_user.id, 'User created!')
            await bot.send_message(message.from_user.id, user.id)


def register_handlers_client(db: Dispatcher):
    db.register_message_handler(db_answer, commands=['start'])
    db.register_message_handler(answer)
