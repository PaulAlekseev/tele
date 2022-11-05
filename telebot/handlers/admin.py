from datetime import datetime, date
from typing import List

from aiogram import types, Dispatcher
from aiogram.types import InputFile

from bot import bot
from entities.async_db.db_engine import async_session
from entities.async_db.db_repos import AIOCredentialDomainRepo, AIOUserRepo, AIOActivationTypeRepo
from entities.async_db.db_specifications import ActivationTypeAllSpecification, ActivationTypeIdSpecification, \
    ActivationTypeActiveSpecification, ActivationTypeSpecification
from entities.functions import form_credentials_admin, form_user_statistics


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


async def get_statistics(message: types.Message):
    async with async_session() as session:
        async with session.begin():
            user_repo = AIOUserRepo(session)
            users = await user_repo.get_all()
            if len(users) == 0:
                await bot.send_message(message.from_user.id, 'No users')
                return 0
            string = form_user_statistics(users)
            text_file = InputFile(path_or_bytesio=string, filename=f'User statistics - {date.today()}.txt')
            await bot.send_document(
                chat_id=message.from_user.id,
                document=text_file,
                caption='Successfully created user statistics',
            )


async def text_all(message: types.Message, regexp):
    async with async_session() as session:
        async with session.begin():
            user_repo = AIOUserRepo(session)
            all_users = await user_repo.get_all()
            for item in all_users:
                await bot.send_message(item.tele_id, regexp.group(1))


async def create_activation_type(message: types.Message, regexp):
    async with async_session() as session:
        async with session.begin():
            activation_type_repo = AIOActivationTypeRepo(session)
            name = ' '.join(regexp.group(1).split('_'))
            amount = regexp.group(2)
            price = regexp.group(3)
            activation_type = await activation_type_repo.create(
                name=name,
                amount=amount,
                price=price
            )
            await bot.send_message(message.from_user.id, f"""Activation type {activation_type.name} has been successfully created
price: {activation_type.price}$/month
amount: {activation_type.amount} credentials/day
""")


async def get_activation_types(message: types.Message, activation_type_specification: ActivationTypeSpecification):
    async with async_session() as session:
        async with session.begin():
            activation_type_repo = AIOActivationTypeRepo(session)
            activation_types = await activation_type_repo.get(activation_type_specification)
            text_header = f"id - name - amount - price:\n"
            text_content = '\n'.join([
                ' - '.join((str(_type.id), _type.name, _type.amount, _type.price, ))
                for _type in activation_types
            ])
            text_result = text_header + text_content
            await bot.send_message(
                message.from_user.id,
                text_result
            )


async def get_all_activation_types(message: types.Message):
    await get_activation_types(message, activation_type_specification=ActivationTypeAllSpecification())


async def get_active_activation_types(message: types.Message):
    await get_activation_types(message, activation_type_specification=ActivationTypeActiveSpecification())


async def change_activation_type_active(message: types.Message, regexp, activity: bool, text: str):
    async with async_session() as session:
        async with session.begin():
            activation_type_repo = AIOActivationTypeRepo(session)
            activation_types = await activation_type_repo.get(ActivationTypeIdSpecification(
                int(regexp.group(1))
            ))
            if len(activation_types) == 0:
                bot.send_message(message.from_user.id, f"There is no activation type with id - {regexp.group(1)}")
            activation_type = activation_types[0]
            activation_type.active = activity
            await activation_type_repo.update(activation_type)
            await bot.send_message(
                message.from_user.id,
                f"Activation type {activation_type.name}({activation_type.id}) has been successfully {text}"
            )


async def activate_activation_type(message: types.Message, regexp):
    await change_activation_type_active(message, regexp, True, text='activated')


async def deactivate_activation_type(message: types.Message, regexp):
    await change_activation_type_active(message, regexp, False, text='deactivated')


def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(get_by_date, regexp='^\/date\s(\d{2}\.\d{2}\.\d{4})-(\d{2}\.\d{2}\.\d{4})')
    dp.register_message_handler(
        text_all,
        regexp=r"^\/send\s([a-zA-Zа-яА-Я\s\d.,?\/\\(\)!@#$%^&*\[\]\{\}';:№`~" + '"]+)'
    )
    dp.register_message_handler(
        create_activation_type,
        regexp=r'^\/create_type\s([\w]+)\s([\d]+)\s([\d]+)'
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
