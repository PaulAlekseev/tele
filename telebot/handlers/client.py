from aiogram import types, Dispatcher

from bot import bot


async def answer(message: types.Message):
    await bot.send_message(message.from_user.id, 'cm')
    a = await message.document.get_file()
    print(await a.get_url())
    print(message.document.file_id)


def register_handlers_client(db: Dispatcher):
    db.register_message_handler(answer, content_types=['document'])
