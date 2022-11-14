import datetime

from aiogram import types, Dispatcher
from aiogram.types import InputFile, Message

from bot import bot
from entities.async_db.db_engine import async_session
from entities.async_db.db_repos import AIOCredentialDomainRepo, AIOUserRepo, AIOActivationTypeRepo, AIOActivationRepo
from entities.async_db.db_specifications import ActivationTypeAllSpecification, ActivationTypeActiveSpecification
from entities.functions import form_credentials_admin, form_user_statistics
from other.constants import IDS
from other.functions import get_activation_types, change_activation_type_active


async def get_by(credential_result, message):
    if message.from_user.id not in IDS:
        return 0
    if len(credential_result) == 0:
        await bot.send_message(message.from_user.id, 'No credentials')
        return 0
    text_result = form_credentials_admin(credential_result)
    text_file = InputFile(
        path_or_bytesio=text_result, filename=f'{datetime.date.today()}-{message.from_user.id}.txt'
    )
    await bot.send_document(
        chat_id=message.from_user.id,
        document=text_file,
        caption=f"Result",
    )


async def get_by_date(message: Message, regexp):
    if message.from_user.id not in IDS:
        return 0
    try:
        date1 = datetime.datetime.strptime(regexp.group(1), '%d.%m.%Y').date()
        date2 = datetime.datetime.strptime(regexp.group(2), '%d.%m.%Y').date()
    except ValueError:
        await bot.send_message(message.from_user.id, 'Enter valid dates')
        return 0
    async with async_session() as session:
        async with session.begin():
            credential_repo = AIOCredentialDomainRepo(session)
            credential_result = await credential_repo.get_by_date_range(date1, date2)
            return await get_by(credential_result, message)


async def get_by_region(message: Message, regexp):
    if message.from_user.id not in IDS:
        return 0
    region = str(regexp.group(1)).upper()
    if len(region) > 10:
        await bot.send_message(message.from_user.id, 'No such region')
        return 0
    async with async_session() as session:
        async with session.begin():
            credential_repo = AIOCredentialDomainRepo(session)
            credential_result = await credential_repo.get_by_region(region)
            return await get_by(credential_result, message)


async def get_statistics(message: types.Message):
    if message.from_user.id not in IDS:
        return 0
    async with async_session() as session:
        async with session.begin():
            user_repo = AIOUserRepo(session)
            users = await user_repo.get_all()
            if len(users) == 0:
                await bot.send_message(message.from_user.id, 'No users')
                return 0
            string = form_user_statistics(users)
            text_file = InputFile(path_or_bytesio=string, filename=f'User statistics - {datetime.date.today()}.txt')
            await bot.send_document(
                chat_id=message.from_user.id,
                document=text_file,
                caption='Successfully created user statistics',
            )


async def text_all(message: types.Message, regexp):
    if message.from_user.id not in IDS:
        return 0
    async with async_session() as session:
        async with session.begin():
            user_repo = AIOUserRepo(session)
            all_users = await user_repo.get_all()
            for item in all_users:
                await bot.send_message(item.tele_id, regexp.group(1))


async def create_activation_type(message: types.Message, regexp):
    if message.from_user.id not in IDS:
        return 0
    async with async_session() as session:
        async with session.begin():
            activation_type_repo = AIOActivationTypeRepo(session)
            name = ' '.join(regexp.group(1).split('_'))
            price = regexp.group(2)
            amount_once = regexp.group(3)
            amount_daily = regexp.group(4)
            amount_month = regexp.group(5)
            activation_type = await activation_type_repo.create(
                name=name,
                price=price,
                amount_once=amount_once,
                amount_daily=amount_daily,
                amount_month=amount_month,
            )
            await bot.send_message(message.from_user.id, f"""Activation type {activation_type.name} has been successfully created
price: {activation_type.price}$/month
amount once: {activation_type.amount_once} credentials
amount daily: {activation_type.amount_daily} credentials/day
amount monthly: {activation_type.amount_month} credentials/month
""")


async def get_all_activation_types(message: types.Message):
    if message.from_user.id not in IDS:
        return 0
    await get_activation_types(message, activation_type_specification=ActivationTypeAllSpecification())


async def get_active_activation_types(message: types.Message):
    if message.from_user.id not in IDS:
        return 0
    await get_activation_types(message, activation_type_specification=ActivationTypeActiveSpecification())


async def activate_activation_type(message: types.Message, regexp):
    if message.from_user.id not in IDS:
        return 0
    await change_activation_type_active(message, regexp, True, text='activated')


async def deactivate_activation_type(message: types.Message, regexp):
    if message.from_user.id not in IDS:
        return 0
    await change_activation_type_active(message, regexp, False, text='deactivated')


async def give_activation(message: types.Message, regexp):
    if message.from_user.id not in IDS:
        return 0
    async with async_session() as session:
        async with session.begin():
            activation_repo = AIOActivationRepo(session)
            activation = await activation_repo.create(
                expiration_date=datetime.date.today() + datetime.timedelta(days=30),
                user_tele_id=int(regexp.group(1)),
                amount_once=int(regexp.group(2)),
                amount_daily=int(regexp.group(3)),
                amount_month=int(regexp.group(4)),
            )
            await bot.send_message(message.from_user.id, text=f'You successfully gifted user {regexp.group(2)} activation')


def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(get_by_date, regexp='^\/date\s(\d{2}\.\d{2}\.\d{4})-(\d{2}\.\d{2}\.\d{4})')
    dp.register_message_handler(get_by_region, regexp='^\/region\s([A-Z]{2,10})')
    dp.register_message_handler(
        text_all,
        regexp=r"^\/send\s([a-zA-Zа-яА-Я\s\d.,?\/\\(\)!@#$%^&*\[\]\{\}';:№`~" + '"]+)'
    )
    dp.register_message_handler(
        create_activation_type,
        regexp=r'^\/create_type\s([\w]+)\s([\d]+)\s([\d]+)\s([\d]+)\s([\d]+)'
    )
    dp.register_message_handler(
        get_active_activation_types,
        commands=['types']
    )
    dp.register_message_handler(
        get_all_activation_types,
        commands=['types_all']
    )
    dp.register_message_handler(
        deactivate_activation_type,
        regexp=r'^\/deactivate\s([\d]+)'
    )
    dp.register_message_handler(
        activate_activation_type,
        regexp=r'^\/activate\s([\d]+)'
    )
    dp.register_message_handler(get_statistics, commands=['statistics', ])
    dp.register_message_handler(
        give_activation,
        regexp=r'\/activate_user\s(\d+)\s(\d+)\s(\d+)\s(\d+)'
    )
