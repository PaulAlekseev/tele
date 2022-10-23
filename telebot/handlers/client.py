import datetime

from aiogram import types, Dispatcher

from bot import bot
from entities.async_db.db_engine import async_session
from entities.async_db.db_repos import AIOCredentialRepo, AIOScanRepo, AIOUserRepository
from entities.async_db.db_specifications import ScanDateUserSpecification, UserTeleIdSpecification, \
    UserSpecification, UserDateSpecification
from tasks import validate, request


# async def answer(message: types.Message):
#     await bot.send_message(message.from_user.id, 'working...')
#     if len(message.text.split('|')) == 3:
#         async with async_session() as session:
#             async with session.begin():
#                 user_repo = UserRepository(session)
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
                user_specification=UserDateSpecification(datetime.date.today()),
            )
            await bot.send_message(message.from_user.id, user)


async def start_scan(message: types.Message):
    async with async_session() as session:
        async with session.begin():
            scan_repo = AIOScanRepo(session)
            user_repo = AIOUserRepository(session)
            file = await bot.get_file(message.document.file_id)
            user = await user_repo.get_user(UserTeleIdSpecification(
                user_tele_id=message.from_user.id
            ))
            scan = await scan_repo.create(
                user_id=user.id,
                file_path=file.file_path,
                file_id=file.file_id,
            )
    await bot.send_message(message.from_user.id, 'Your scan has been successfully created')
    await bot.send_message(message.from_user.id, scan)
    validate.delay()


async def get_scans(message: types.Message):
    async with async_session() as session:
        async with session.begin():
            scan_repo = AIOScanRepo(session)
            user_repo = AIOUserRepository(session)
            user = await user_repo.get_user(UserTeleIdSpecification(message.from_user.id))
            scans = await scan_repo.get_with(
                ScanDateUserSpecification(
                    user_id=user.id,
                    scan_date=datetime.date.today())
            )
            await bot.send_message(message.from_user.id, scans)


async def trigger_scan(message: types.Message):
    validate.delay()


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
    db.register_message_handler(start_scan, content_types=['document'])
    db.register_message_handler(get_scans, commands=['scans'])
    db.register_message_handler(trigger_scan, commands=['trigger'])
    # db.register_message_handler(create_user, commands=['create'])
    # db.register_message_handler(document, content_types=['document'])
    # db.register_message_handler(answer)
