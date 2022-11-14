import datetime

import emoji
from typing import List, Dict

from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

from bot import bot
from entities.async_db.db_engine import async_session
from entities.async_db.db_repos import AIOActivationTypeRepo
from entities.async_db.db_specifications import ActivationTypeSpecification, ActivationTypeIdSpecification
from entities.async_db.db_tables import ActivationType, Activation


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
    keyboard.row(
        *[KeyboardButton(text=emoji.emojize(key)) for key in button_str_list[0:2]]
    )
    keyboard.add(
        *[KeyboardButton(text=emoji.emojize(key)) for key in button_str_list[2:]]
    )
    return keyboard


async def get_activation_types(message: types.Message, activation_type_specification: ActivationTypeSpecification):
    async with async_session() as session:
        async with session.begin():
            activation_type_repo = AIOActivationTypeRepo(session)
            activation_types = await activation_type_repo.get(activation_type_specification)
            text_header = f"id - name - price - amount: once - daily - monthly\n"
            text_content = '\n'.join([
                ' - '.join(
                    (str(_type.id), _type.name, _type.price, _type.amount_once, _type.amount_daily, _type.amount_month)
                )
                for _type in activation_types
            ])
            text_result = text_header + text_content
            await bot.send_message(
                message.from_user.id,
                text_result
            )


async def change_activation_type_active(message: types.Message, regexp, activity: bool, text: str):
    async with async_session() as session:
        async with session.begin():
            activation_type_repo = AIOActivationTypeRepo(session)
            activation_types = await activation_type_repo.get(ActivationTypeIdSpecification(
                int(regexp.group(1))
            ))
            if len(activation_types) == 0:
                await bot.send_message(message.from_user.id, f"There is no activation type with id - {regexp.group(1)}")
                return 0
            activation_type = activation_types[0]
            activation_type.active = activity
            await activation_type_repo.update(activation_type)
            await bot.send_message(
                message.from_user.id,
                f"Activation type {activation_type.name}({activation_type.id}) has been successfully {text}"
            )


def form_activation_type_tariffs(data: List[ActivationType], lang: str):
    keyboard_markup = InlineKeyboardMarkup(row_width=1)
    keyboard_markup.add(
        *[InlineKeyboardButton(
            text=f'{item.name} - price: {item.price} - amount: once: {item.amount_once} - daily: {item.amount_daily} - monthly: {item.amount_month}', callback_data=f'type-{item.id}-{lang}'
        ) for item in data]
    )
    return keyboard_markup


def form_payment_markup(data: List[str], activation_type_id: str, lang: str) -> InlineKeyboardMarkup:
    keyboard_markup = InlineKeyboardMarkup(row_width=1)
    keyboard_markup.add(
        *[InlineKeyboardButton(
            text=f'{item}', callback_data=f'final_pay-{item}-{activation_type_id}-{lang}'
        ) for item in data]
    )
    return keyboard_markup


def check_and_update_activation(activation: Activation) -> dict:
    result = {
        'amount': 0,
        'error': None
    }
    if activation.date_check < datetime.date.today():
        activation.amount_check = activation.amount_daily
        activation.date_check = datetime.date.today()
        result['amount'] = activation.amount_daily
    if activation.amount_check > 0 and activation.amount_month > 0:
        if activation.amount_check >= activation.amount_month:
            result['amount'] = activation.amount_check
    elif activation.amount_month <= 0:
        result['error'] = 1
    else:
        result['error'] = 0
    result['activation'] = activation
    return result
