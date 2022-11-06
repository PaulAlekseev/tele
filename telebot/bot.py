import os

from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.webhook import DEFAULT_ROUTE_NAME
from aiogram.utils.executor import set_webhook

# webhook settings
WEBHOOK_HOST = 'https://awshosttest.site/'
WEBHOOK_PATH = ''
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# webserver settings
WEBAPP_HOST = 'localhost'  # or ip
WEBAPP_PORT = 3001


bot = Bot(os.getenv('TOKEN'))
dp = Dispatcher(bot)

if __name__ == '__main__':
    executor = set_webhook(dispatcher=dp,
                           webhook_path=WEBHOOK_PATH,
                           loop=None,
                           skip_updates=None,
                           check_ip=False,
                           retry_after=None,
                           route_name=DEFAULT_ROUTE_NAME,
                           )
    executor.run_app(host=WEBAPP_HOST, port=WEBAPP_PORT)
