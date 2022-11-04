from datetime import datetime

from aiogram import types, Dispatcher
from aiogram.types import InputFile

from bot import bot
from entities.async_db.db_engine import async_session
from entities.async_db.db_repos import AIOCredentialDomainRepo, AIOUserRepo
from entities.functions import form_credentials_admin


async def get_by_date(message: types.Message, regexp):
    try:
        date1 = datetime.strptime(regexp.group(1), '%d.%m.%Y').date()
        date2 = datetime.strptime(regexp.group(2), '%d.%m.%Y').date()
    except ValueError:
        await bot.send_message(message.from_user.id, 'Enter valid dates')
        return 0
    async with async_session() as session:
        async with session.begin():
            credential_repo = AIOCredentialDomainRepo(session)
            credential_result = await credential_repo.get_by_date_range(date1, date2)
            if len(credential_result) == 0:
                await bot.send_message(message.from_user.id, 'No credentials this dates')
                return 0
            text_result = form_credentials_admin(credential_result)
            text_file = InputFile(
                path_or_bytesio=text_result, filename=f'{datetime.now()}-{message.from_user.id}.txt'
            )
            await bot.send_document(
                chat_id=message.from_user.id,
                document=text_file,
                caption=f"Data from {date1} to {date2}",
            )


async def text_all(message: types.Message, regexp):
    async with async_session() as session:
        async with session.begin():
            user_repo = AIOUserRepo(session)
            all_users = await user_repo.get_all()
            for item in all_users:
                await bot.send_message(item.tele_id, regexp.group(1))


def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(get_by_date, regexp='^date\s(\d{2}\.\d{2}\.\d{4})-(\d{2}\.\d{2}\.\d{4})')
    dp.register_message_handler(
        text_all,
        regexp=r"^send\s([a-zA-Zа-яА-Я\s\d.,?\/\\(\)!@#$%^&*\[\]\{\}';:№`~]+)"
    )
