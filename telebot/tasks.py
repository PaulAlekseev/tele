import asyncio
import time

from bot import bot
from celery_app import app
from entities.db.db_repos import CredentialsRepository, ScanRepository
from entities.db.db_tables import Scan
from entities.user import User
from entities.validator import APIValidator


@app.task
def add(message: str):
    print(message.split())
    time.sleep(5)
    print('bruh')


@app.task
def validate(scan_id: int):
    time.sleep(10)
    print(scan_id)
    # sync_send_message(message=message_splited[0] + ' done!', chat_id=user_id)


async def send_message(message, chat_id):
    await bot.send_message(chat_id=chat_id, text=message)


def sync_send_message(message, chat_id):
    asyncio.run(send_message(chat_id=chat_id, message=message))


@app.task
def request():
    repo = CredentialsRepository()
    result = repo.get_by_session(1)
    print(result)
