import datetime

from aiogram import types, Dispatcher
import emoji
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot import bot
from entities.async_db.db_engine import async_session
from entities.async_db.db_repos import AIOCredentialRepo, AIOScanRepo, AIOActivationRepo
from entities.async_db.db_specifications import ScanDateUserSpecification
from entities.db.db_repos import ScanRepository
from other.functions import create_reply_markup
from other.markups import language_markup
from other.text_dicts import main_menu_text, scan_text, activation_text, profile_text
from tasks import get_file_credentials, validate_short, validate


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
                text_dict['text'].format(
                    message.from_user.id,
                    text_dict['active']['good'] if active else text_dict['active']['bad'],
                    latest_activation.expires if active else '-',
                )
            )


async def start_scan(message: types.Message):
    # async with async_session() as session:
    #     async with session.begin():
    #         scan_repo = AIOScanRepo(session)
    #         file = await bot.get_file(message.document.file_id)
    #         scan = await scan_repo.create(
    #             user_tele_id=message.from_user.id,
    #             file_path=file.file_path,
    #             file_id=file.file_id,
    #         )
    if message.caption not in scan_text:
        return 0
    text_markup = scan_text[message.caption]
    async with async_session() as session:
        async with session.begin():
            activation_repo = AIOActivationRepo(session)
            latest_activation = await activation_repo.get_latest(user_tele_id=message.from_user.id)
        inline_keyboard = InlineKeyboardMarkup(row_width=1)
        if latest_activation:
            if latest_activation.expires >= datetime.date.today():
                inline_keyboard.add(InlineKeyboardButton(text_markup['start'], callback_data=text_markup['button']['good']))
                text = text_markup['text']['good']
            else:
                inline_keyboard.add(InlineKeyboardButton(text_markup['no_activation'], callback_data=text_markup['button']['bad']))
                text = text_markup['text']['bad']
        else:
            inline_keyboard.add(InlineKeyboardButton(text_markup['no_activation'], callback_data=text_markup['button']['bad']))
            text = text_markup['text']['bad']
    await message.reply(text=text, reply_markup=inline_keyboard)


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
        start_scan,
        content_types=['document'],
    )
    dp.register_message_handler(
        profile,
        lambda message: emoji.demojize(message.text) in profile_text
    )
    dp.register_message_handler(get_scans, commands=['scans'])
    dp.register_message_handler(start, lambda message: emoji.demojize(message.text) in (
            ':reverse_button: Back to languages',
            ':reverse_button: Назад к выбору языка',
    ))
    dp.register_message_handler(start, commands=['start', ])
    dp.register_message_handler(main_menu, lambda message: emoji.demojize(message.text) in main_menu_text)
    dp.register_message_handler(create_activation, lambda message: message.text in activation_text)
    dp.register_callback_query_handler(create_activation, lambda c: c.data in activation_text)
