import asyncio
import os

import requests

from bot import bot
from celery import Celery
from other.constants import IDS

app = Celery(
    'tele',
    broker='redis://redis:6379/0',
    include=['tasks', ]
)


# app.conf.timezone = 'Europe/London'


# @app.on_after_configure.connect
# def setup_periodic_tasks(sender, **kwargs):
#     sender.add_periodic_task(60, check_other.s(), expires=15)


async def send_message(message, chat_id):
    await bot.send_message(chat_id=chat_id, text=message)


def sync_send_message(message, chat_id):
    asyncio.run(send_message(chat_id=chat_id, message=message))


@app.task
def check_other():
    try:
        result = requests.get(os.getenv('OTHER_HOST') + 'api/check')
        if result.status_code == 200:
            return 0
        else:
            raise Exception
    except Exception:
        for id_ in IDS:
            sync_send_message(
                "Store not working",
                id_,
            )
