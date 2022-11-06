import os

from aiogram import Bot
from aiogram.dispatcher import Dispatcher


# webhook settings
WEBHOOK_HOST = 'https://awshosttest.site/'
WEBHOOK_PATH = ''
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# webserver settings
WEBAPP_HOST = '127.0.0.1'  # or ip
WEBAPP_PORT = 3001


bot = Bot(os.getenv('TOKEN'))
dp = Dispatcher(bot)
