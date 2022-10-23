import datetime

from aiogram import types, Dispatcher

from bot import bot
from entities.async_db.db_engine import async_session
from entities.async_db.db_repos import AIOCredentialRepo, AIOScanRepo, AIOUserRepository
from entities.async_db.db_specifications import AIOScanDateUserSpecification, AIOUserTeleIdSpecification, \
    AIOUserSpecification, AIOUserDateSpecification
from tasks import validate, request


# async def answer(message: types.Message):
#     await bot.send_message(message.from_user.id, 'working...')
#     if len(message.text.split('|')) == 3:
#         async with async_session() as session:
#             async with session.begin():
#                 user_repo = AIOUserRepository(session)
#                 user = await user_repo.create(message.from_user.id)
#         validate.delay(message.text, user.id)
#     else:
#         request.delay()


async def db_answer(message: types.Message):
    async with async_session() as session:
        async with session.begin():
            # Creating user row in database
            user_repo = AIOUserRepository(session)
            await user_repo.create(message.from_user.id)

            # answer
            await bot.send_message(message.from_user.id, 'Your account has been successfully created')


async def get_user(message: types.Message):
    async with async_session() as session:
        async with session.begin():
            user_repo = AIOUserRepository(session)
            user = await user_repo.get_user(
                user_specification=AIOUserDateSpecification(datetime.date.today()),
            )
            await bot.send_message(message.from_user.id, [(item.id, item.user_id, item.created, ) for item in user])
#
#
# async def create_user(message: types.Message):
#     async with async_session() as session:
#         async with session.begin():
#             user_repo = AIOUserRepository(session)
#             user = await user_repo.create(message.from_user.id)
#             await bot.send_message(message.from_user.id, 'User created!')
#             await bot.send_message(message.from_user.id, user.id)


# async def document(message: types.Message):
#     file = await bot.get_file(message.document.file_id)
#     await bot.send_message(message.from_user.id, file.file_path)
#     await bot.send_message(message.from_user.id, file.file_id)


# async def get_document(message: types.Message):
#
#     await bot.send_message(message.from_user.id, )


def register_handlers_client(db: Dispatcher):
    db.register_message_handler(db_answer, commands=['start'])
    db.register_message_handler(get_user, commands=['get'])
    # db.register_message_handler(create_user, commands=['create'])
    # db.register_message_handler(document, content_types=['document'])
    # db.register_message_handler(answer)

