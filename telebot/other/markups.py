from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import emoji

from other.text_dicts import main_menu_text


language_markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
language_markup.row(*[
    KeyboardButton(text=emoji.emojize(key)) for key in main_menu_text.keys()
])
