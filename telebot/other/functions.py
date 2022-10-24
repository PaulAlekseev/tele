from typing import List

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import emoji


def create_reply_markup(
        button_str_list: List[str],
        one_time_keyboard: bool,
        row_width: int
) -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True,
        one_time_keyboard=one_time_keyboard,
        row_width=row_width,
    )
    keyboard.add(
        *[KeyboardButton(text=emoji.emojize(key)) for key in button_str_list]
    )
    return keyboard
