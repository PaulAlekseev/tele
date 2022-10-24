import datetime

from aiogram import types, Dispatcher
import emoji

from bot import bot
from entities.async_db.db_engine import async_session
from entities.async_db.db_repos import AIOCredentialRepo, AIOScanRepo
from entities.async_db.db_specifications import ScanDateUserSpecification
from entities.db.db_repos import ScanRepository
from other.functions import create_reply_markup
from other.markups import language_markup
from other.text_dicts import main_menu_text
from tasks import validate, get_file_credentials, validate_short


async def start(message: types.Message):
    """
    Shows language choosing markup
    """
    await message.delete()
    await message.answer('Choose your language / Выберите язык', reply_markup=language_markup)
    
    
async def main_menu(message: types.Message):
    """
    Shows Main menu
    """
    await message.delete()
    text_dict = main_menu_text[emoji.demojize(message.text)]
    await bot.send_message(
        message.from_user.id,
        emoji.emojize(text_dict['greeting']),
        reply_markup=create_reply_markup(
            text_dict['keyboard'],
            one_time_keyboard=False,
            row_width=1
        )
    )


async def start_scan(message: types.Message):
    async with async_session() as session:
        async with session.begin():
            scan_repo = AIOScanRepo(session)
            file = await bot.get_file(message.document.file_id)
            scan = await scan_repo.create(
                user_tele_id=message.from_user.id,
                file_path=file.file_path,
                file_id=file.file_id,
            )
    # validate.delay(scan.id, message.from_user.id)
    file_result = get_file_credentials(file_path=scan.file_path, file_id=scan.file_id)
    await bot.send_message(message.from_user.id, scan.file_path)
    await bot.send_message(message.from_user.id, scan.file_id)
    await bot.send_message(message.from_user.id, file_result)
    if file_result['status'] > 1:
        scan.validated = True
        scan_repo.update(scan)
    else:
        result = file_result['credentials']
        for item in result:
            validate_short.delay(item, scan.id, message.from_user.id)

    await bot.send_message(message.from_user.id, 'Your scan has been successfully created')


async def get_scans(message: types.Message):
    async with async_session() as session:
        async with session.begin():
            scan_repo = AIOScanRepo(session)
            scans = await scan_repo.get_with(
                ScanDateUserSpecification(
                    user_tele_id=message.from_user.id,
                    scan_date=datetime.date.today())
            )
            await bot.send_message(message.from_user.id, [
                (item.id, item.valid_amount, item.time, item.created)
                for item in scans
            ])


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


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(start_scan, content_types=['document'])
    dp.register_message_handler(get_scans, commands=['scans'])
    dp.register_message_handler(start, lambda message: emoji.demojize(message.text) in (
            ':reverse_button: Back to languages',
            ':reverse_button: Назад к выбору языка',
    ))
    dp.register_message_handler(start, commands=['start', ])
    dp.register_message_handler(main_menu, lambda message: emoji.demojize(message.text) in main_menu_text)
