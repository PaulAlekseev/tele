import datetime

from aiogram import types, Dispatcher
import emoji
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot import bot
from entities.async_db.db_engine import async_session
from entities.async_db.db_repos import AIOActivationRepo, AIOUserRepo, AIOActivationTypeRepo
from entities.async_db.db_specifications import ActivationTypeActiveSpecification, ActivationTypeIdSpecification
from other.functions import create_reply_markup, form_activation_type_tariffs, form_payment_markup, \
    check_and_update_activation
from other.markups import language_markup
from other.text_dicts import main_menu_text, scan_text, activation_text, profile_text, activation_tariffs_text, \
    available_crypto, crypto_payment_choice, support_text, rules_text
from tasks import validate


async def start(message: types.Message):
    """
    Shows language choosing markup
    """
    async with async_session() as session:
        async with session.begin():
            user_repo = AIOUserRepo(session)
            await user_repo.create(str(message.from_user.id))
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
    await bot.send_message(
        message.from_user.id,
        text=text_dict['instructions']
    )


async def profile(message: types.Message):
    """
    Shows Profile
    """
    await message.delete()
    async with async_session() as session:
        async with session.begin():
            activation_repo = AIOActivationRepo(session)
            latest_activation = await activation_repo.get_latest(message.from_user.id)
            activation_exist = True if latest_activation else False
            active = True if activation_exist and latest_activation.expires >= datetime.date.today() else False
            text_dict = profile_text[emoji.demojize(message.text)]
            await bot.send_message(
                message.from_user.id,
                emoji.emojize(text_dict['text'].format(
                    message.from_user.id,
                    text_dict['active']['good'] if active else text_dict['active']['bad'],
                    latest_activation.expires if active else '-',
                ))
            )


async def support(message: types.Message):
    """
    Shows support
    """
    await message.delete()
    text = support_text[emoji.demojize(message.text)]
    await bot.send_message(message.from_user.id, text=text['text'])


async def rules(message: types.Message):
    """
    Shows rules
    """
    await message.delete()
    text = rules_text[emoji.demojize(message.text)]
    await bot.send_message(message.from_user.id, text=text['text'])



async def file_handler(message: types.Message):
    if message.caption not in scan_text:
        return 0
    text_markup = scan_text[message.caption]

    # Getting latest activation
    async with async_session() as session:
        async with session.begin():
            activation_repo = AIOActivationRepo(session)
            latest_activation = await activation_repo.get_latest(user_tele_id=message.from_user.id)

    # Checking if scan is allowed
    inline_keyboard = InlineKeyboardMarkup(row_width=1)
    all_good = False
    if latest_activation:
        if latest_activation.expires >= datetime.date.today():
            checked_activation = check_and_update_activation(latest_activation)
            if not checked_activation['result']:
                await bot.send_message(message.from_user.id, text_markup['activation_failure'])
                return 0
            all_good = True
            text = text_markup['text']['good'].format(str(checked_activation['amount']), )
            await start_scan(
                message=message,
                lang=message.caption,
                amount=checked_activation['amount'],
                activation_id=latest_activation.id,
            )
        else:
            inline_keyboard.add(
                InlineKeyboardButton(text_markup['no_activation'], callback_data=text_markup['button']['bad']))
            text = text_markup['text']['bad']
    else:
        inline_keyboard.add(
            InlineKeyboardButton(text_markup['no_activation'], callback_data=text_markup['button']['bad']))
        text = text_markup['text']['bad']
    await message.reply(text=text, reply_markup=inline_keyboard if not all_good else None)


async def start_scan(message: types.Message, lang: str, amount: int, activation_id: int):
    async with async_session() as session:
        async with session.begin():
            file = await bot.get_file(message.document.file_id)
            validate.delay(
                scan_file_id=file.file_id,
                scan_file_path=file.file_path,
                user_id=message.from_user.id,
                lang=lang,
                activation_amount=amount,
                activation_id=activation_id,
            )


async def create_activation(callback_query: types.CallbackQuery):
    async with async_session() as session:
        async with session.begin():
            activation_repo = AIOActivationRepo(session)
            activation = await activation_repo.create(
                expiration_date=datetime.date.today() + datetime.timedelta(days=30),
                user_tele_id=callback_query.from_user.id,
                amount=100
            )
            await bot.send_message(callback_query.from_user.id, text=activation_text[callback_query.data])


async def get_activation_type_tariffs(message: types.Message):
    async with async_session() as session:
        async with session.begin():
            active_text = activation_tariffs_text[emoji.demojize(message.text)]
            activation_type_repo = AIOActivationTypeRepo(session)
            activation_types = await activation_type_repo.get(ActivationTypeActiveSpecification())
            keyboard = form_activation_type_tariffs(
                data=activation_types,
                lang=active_text['lang']
            )
            await bot.send_message(
                message.from_user.id, reply_markup=keyboard, text=active_text['text'])


async def choose_payment_coin(callback_query: types.CallbackQuery, regexp):
    await callback_query.message.delete()
    crypto_choice = crypto_payment_choice[regexp.group(2)]
    await bot.send_message(
        callback_query.from_user.id,
        reply_markup=form_payment_markup(
            data=available_crypto,
            activation_type_id=regexp.group(1),
            lang=regexp.group(2)
        ),
        text=crypto_choice['text']
    )


async def payment_start(callback_query: types.CallbackQuery, regexp):
    await callback_query.message.delete()
    async with async_session() as session:
        async with session.begin():
            activation_type_repo = AIOActivationTypeRepo(session)
            activation_types = await activation_type_repo.get(
                ActivationTypeIdSpecification(int(regexp.group(2)))
            )
            activation_type = activation_types[0]
            await bot.send_message(
                chat_id=callback_query.from_user.id,
                text=f'{activation_type.id} - {activation_type.active} - {activation_type.name} - {activation_type.price}'
            )


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(
        file_handler,
        content_types=['document'],
    )
    dp.register_message_handler(
        profile,
        lambda message: emoji.demojize(message.text) in profile_text
    )
    dp.register_message_handler(start, lambda message: emoji.demojize(message.text) in (
        ':reverse_button: Back to languages',
        ':reverse_button: Назад к выбору языка',
    ))
    dp.register_message_handler(start, commands=['start', ])
    dp.register_message_handler(main_menu, lambda message: emoji.demojize(message.text) in main_menu_text)
    dp.register_message_handler(
        get_activation_type_tariffs,
        lambda message: emoji.demojize(message.text) in [':key: Активировать', ':key: Activate']
    )
    dp.register_callback_query_handler(create_activation, lambda c: c.data in activation_text)
    dp.register_callback_query_handler(
        choose_payment_coin,
        regexp=r"^type-(\d+)-(rus|eng)"
    )
    dp.register_callback_query_handler(
        payment_start,
        regexp=r"^final_pay-(\w+)-(\d+)-(\w{3})"
    )
    dp.register_message_handler(rules, lambda message: emoji.demojize(message.text) in rules_text)
    dp.register_message_handler(support, lambda message: emoji.demojize(message.text) in support_text)
