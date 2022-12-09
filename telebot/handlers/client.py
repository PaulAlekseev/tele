import datetime

import aiohttp
from aiogram import types, Dispatcher
import emoji
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot import bot
from entities.async_db.db_engine import async_session
from entities.async_db.db_repos import AIOActivationRepo, AIOUserRepo, AIOActivationTypeRepo
from entities.async_db.db_specifications import ActivationTypeActiveSpecification, ActivationTypeIdSpecification
from other.constants import AMOUNT_DAILY, AMOUNT_MONTHLY, AMOUNT_ONCE
from other.functions import create_reply_markup, form_activation_type_tariffs, form_payment_markup, \
    check_and_update_activation
from other.invoice import Invoice, QiwiInvoice
from other.markups import language_markup
from other.text_dicts import main_menu_text, scan_text, activation_text, profile_text, activation_tariffs_text, \
    available_crypto, crypto_payment_choice, support_text, rules_text, crypto_payment_start_choice, activate_text_dict
from tasks import validate


async def start(message: types.Message):
    """
    Shows language choosing markup
    """
    try:
        async with async_session() as session:
            async with session.begin():
                user_repo = AIOUserRepo(session)
                await user_repo.create(str(message.from_user.id))
        await message.answer('Choose your language / Выберите язык', reply_markup=language_markup)
    except Exception:
        pass


async def main_menu(message: types.Message):
    """
    Shows Main menu
    """
    try:
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
    except Exception:
        pass


async def profile(message: types.Message):
    """
    Shows Profile
    """
    try:
        async with async_session() as session:
            async with session.begin():
                activation_repo = AIOActivationRepo(session)
                latest_activation = await activation_repo.get_latest(str(message.from_user.id))
                activation_exist = True if latest_activation else False
                active = True if activation_exist and latest_activation.expires >= datetime.date.today() else False
                text_dict = profile_text[emoji.demojize(message.text)]
                await bot.send_message(
                    message.from_user.id,
                    emoji.emojize(text_dict['text'].format(
                        message.from_user.id,
                        text_dict['active']['good'] if active else text_dict['active']['bad'],
                        latest_activation.expires if active else '-',
                    )))
    except Exception:
        pass


async def support(message: types.Message):
    """
    Shows support
    """
    try:
        text = support_text[emoji.demojize(message.text)]
        await bot.send_message(message.from_user.id, text=text['text'])
    except Exception:
        pass


async def rules(message: types.Message):
    """
    Shows rules
    """
    try:
        text = rules_text[emoji.demojize(message.text)]
        await bot.send_message(message.from_user.id, text=text['text'])
    except Exception:
        pass


async def file_handler(message: types.Message):
    try:
        if message.caption not in scan_text:
            return 0
        text_markup = scan_text[message.caption]

        # Getting latest activation
        async with async_session() as session:
            async with session.begin():
                activation_repo = AIOActivationRepo(session)
                latest_activation = await activation_repo.get_latest(user_tele_id=str(message.from_user.id))
                user_repo = AIOUserRepo(session)
                await user_repo.create(str(message.from_user.id))

        # Checking if scan is allowed
        inline_keyboard = InlineKeyboardMarkup(row_width=1)
        all_good = False
        if latest_activation:
            if latest_activation.expires >= datetime.date.today():
                checked_activation = await check_and_update_activation(latest_activation)
                if checked_activation['error']:
                    await bot.send_message(
                        message.from_user.id, text_markup['activation_failure'][checked_activation['error']]
                    )
                    return 0
                all_good = True
                text = text_markup['text']['good'].format(str(latest_activation.amount_check), )
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
    except Exception:
        pass


async def start_scan(message: types.Message, lang: str, amount: int, activation_id: int):
    try:
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
    except Exception:
        pass


async def create_activation(user_tele_id: int, callback_data: str):
    try:
        async with async_session() as session:
            async with session.begin():
                activation_repo = AIOActivationRepo(session)
                activation = await activation_repo.get_latest(str(user_tele_id))
                if activation:
                    if activation.expires >= datetime.date.today():
                        await bot.send_message(
                            user_tele_id,
                            activation_text[callback_data]['bad'],
                        )
                        return 0
                activation = await activation_repo.create(
                    expiration_date=datetime.date.today() + datetime.timedelta(days=30),
                    user_tele_id=str(user_tele_id),
                    amount_once=AMOUNT_ONCE,
                    amount_daily=AMOUNT_DAILY,
                    amount_month=AMOUNT_MONTHLY
                )
                await bot.send_message(user_tele_id, text=activation_text[callback_data]['good'])
    except Exception:
        pass


async def create_activation_from_callback(callback_query: types.CallbackQuery):
    try:
        await create_activation(
            user_tele_id=callback_query.from_user.id,
            callback_data=callback_query.data,
        )
    except Exception:
        pass


async def create_activation_from_message(message: types.Message):
    try:
        text_data = activate_text_dict[emoji.demojize(message.text)]
        await create_activation(
            user_tele_id=message.from_user.id,
            callback_data=text_data,
        )
    except Exception:
        pass


async def get_activation_type_tariffs(message: types.Message):
    try:
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
    except Exception:
        pass


async def choose_payment_coin(callback_query: types.CallbackQuery, regexp):
    try:
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
    except Exception:
        pass


async def payment_start(callback_query: types.CallbackQuery, regexp):
    try:
        await callback_query.message.delete()
        async with async_session() as session:
            async with session.begin():
                text = crypto_payment_start_choice[regexp.group(3)]
                activation_type_repo = AIOActivationTypeRepo(session)
                activation_types = await activation_type_repo.get(
                    ActivationTypeIdSpecification(int(regexp.group(2)))
                )
                activation_type = activation_types[0]
                if not activation_type.active:
                    await bot.send_message(
                        chat_id=callback_query.from_user.id,
                        text=text['fail_text']
                    )
                    return 0
                crypto_credentials = available_crypto[regexp.group(1)]
                async with aiohttp.ClientSession() as client_session:
                    invoice = Invoice(
                        amount=str(activation_type.price),
                        api_key=crypto_credentials['API-key'],
                        password=crypto_credentials['password'],
                        session=client_session,
                        tele_id=callback_query.from_user.id,
                        token_name=regexp.group(1),
                        custom_data=str(activation_type.id)
                        )
                    await invoice.create_invoice()
                await bot.send_message(
                    chat_id=callback_query.from_user.id,
                    text=await invoice.get_url()
                )
    except Exception:
        pass


async def create_qiwi_invoice(message: types.Message, regexp):
    try:
        async with aiohttp.ClientSession() as session:
            invoice = QiwiInvoice(
                user_tele_id=message.from_user.id,
                price=1,
                time_expiration_hours=int(regexp.group(1)),
                comment="hello",
                session=session,
            )
            try:
                invoice_result = await invoice.create_invoice()
                await bot.send_message(
                    chat_id=message.from_user.id,
                    text=f"Your invoice has been successfully created {invoice_result['payUrl']}"
                )
            except Exception:
                return 0
    except Exception:
        pass


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(
        create_qiwi_invoice,
        regexp=r'\/qiwi\s(\d+)'
    )
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
    # dp.register_message_handler(
    #     get_activation_type_tariffs,
    #     lambda message: emoji.demojize(message.text) in [':key: Активировать', ':key: Activate']
    # )
    dp.register_callback_query_handler(create_activation_from_callback, lambda c: c.data in activation_text)
    dp.register_callback_query_handler(
        choose_payment_coin,
        regexp=r"^type-(\d+)-(rus|eng)"
    )
    dp.register_callback_query_handler(
        payment_start,
        regexp=r"^final_pay-(\w+)-(\d+)-(rus|eng)"
    )
    dp.register_message_handler(rules, lambda message: emoji.demojize(message.text) in rules_text)
    dp.register_message_handler(support, lambda message: emoji.demojize(message.text) in support_text)
    dp.register_message_handler(
        create_activation_from_message,
        lambda message: emoji.demojize(message.text) in activate_text_dict,
    )
