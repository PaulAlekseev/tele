import os

from aiogram import Bot
from aiogram.dispatcher import Dispatcher


# webhook settings
WEBHOOK_HOST = 'https://awshosttest.site/'
WEBHOOK_PATH = ''
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# webserver settings
WEBAPP_HOST = 'localhost'  # or ip
WEBAPP_PORT = 3000


bot = Bot(os.getenv('TOKEN'))
dp = Dispatcher(bot)
