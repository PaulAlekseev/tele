import asyncio
import multiprocessing
import os
import time
from concurrent.futures import ThreadPoolExecutor

from bot import bot
from celery_app import app
from entities.async_db.db_specifications import ScanIdSpecification
from entities.db.db_repos import CredentialsRepository, ScanRepository


@app.task
def add(message: str):
    print(message.split())
    time.sleep(5)
    print('bruh')


@app.task
def validate(scan_id: int, user_id):
    sync_send_message(message=f"Your scan {scan_id}, has been started", chat_id=user_id)
    # Getting data from document
    scan_repo = ScanRepository()
    scan = scan_repo.get(
        ScanIdSpecification(scan_id=scan_id)
    )[0]

    sync_send_message(message=f"""Scan file id: {scan.file_id}
Scan file path: {scan.file_path}
Bot id: {os.getenv('BOT_TOKEN')}
""", chat_id=user_id)

    # cpu_count = multiprocessing.cpu_count()
    # with ThreadPoolExecutor(max_workers=cpu_count-2 if cpu_count>3 else cpu_count) as executor:
    #     for item in


async def send_message(message, chat_id):
    await bot.send_message(chat_id=chat_id, text=message)


def sync_send_message(message, chat_id):
    asyncio.run(send_message(chat_id=chat_id, message=message))


@app.task
def request():
    repo = CredentialsRepository()
    result = repo.get_by_session(1)
    print(result)
