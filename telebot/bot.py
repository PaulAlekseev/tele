import os

from aiogram import Bot
from aiogram.dispatcher import Dispatcher


bot = Bot(os.getenv('TOKEN'))
dp = Dispatcher(bot)
