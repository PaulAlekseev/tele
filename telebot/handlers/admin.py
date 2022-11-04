from datetime import datetime

from aiogram import types, Dispatcher

from bot import bot
from entities.async_db.db_engine import async_session
from entities.async_db.db_repos import AIOCredentialDomainRepo


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
            credential_result = credential_repo.get_by_date_range(date1, date2)
            await bot.send_message(
                message.from_user.id,
                str(credential_result)
            )


def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(get_by_date, regexp='^date\s(\d{2}\.\d{2}\.\d{4})-(\d{2}\.\d{2}\.\d{4})')
