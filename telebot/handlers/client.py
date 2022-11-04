import datetime

from aiogram import types, Dispatcher
import emoji
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot import bot
from entities.async_db.db_engine import async_session
from entities.async_db.db_repos import AIOActivationRepo, AIOUserRepo
from other.functions import create_reply_markup
from other.markups import language_markup
from other.text_dicts import main_menu_text, scan_text, activation_text, profile_text
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


async def file_handler(message: types.Message):
    if message.caption not in scan_text:
        return 0
    text_markup = scan_text[message.caption]
    async with async_session() as session:
        async with session.begin():
            activation_repo = AIOActivationRepo(session)
            latest_activation = await activation_repo.get_latest(user_tele_id=message.from_user.id)
    inline_keyboard = InlineKeyboardMarkup(row_width=1)
    all_good = False
    if latest_activation:
        if latest_activation.expires >= datetime.date.today():
            all_good = True
            text = text_markup['text']['good']
            await start_scan(message, message.caption)
        else:
            inline_keyboard.add(InlineKeyboardButton(text_markup['no_activation'], callback_data=text_markup['button']['bad']))
            text = text_markup['text']['bad']
    else:
        inline_keyboard.add(InlineKeyboardButton(text_markup['no_activation'], callback_data=text_markup['button']['bad']))
        text = text_markup['text']['bad']
    await message.reply(text=text, reply_markup=inline_keyboard if not all_good else None)


async def start_scan(message: types.Message, lang: str):
    async with async_session() as session:
        async with session.begin():
            file = await bot.get_file(message.document.file_id)
            validate.delay(
                scan_file_id=file.file_id,
                scan_file_path=file.file_path,
                user_id=message.from_user.id,
                lang=lang
            )


async def create_activation(callback_query: types.CallbackQuery):
    async with async_session() as session:
        async with session.begin():
            activation_repo = AIOActivationRepo(session)
            activation = await activation_repo.create(
                expiration_date=datetime.date.today() + datetime.timedelta(days=30),
                user_tele_id=callback_query.from_user.id
            )
            await bot.send_message(callback_query.from_user.id, text=activation_text[callback_query.data])


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
    dp.register_callback_query_handler(create_activation, lambda c: c.data in activation_text)
