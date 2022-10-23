import asyncio
import multiprocessing
import os
import time

import requests

from bot import bot
from celery_app import app
from entities.constants import FILE_API_URL
from entities.db.db_repos import CredentialsRepository, ScanRepository


@app.task
def add(message: str):
    print(message.split())
    time.sleep(5)
    print('bruh')


def get_file_credentials(file_path: str, file_id: str) -> dict:
    result = {
        'status': 1,
        'credentials': [],
        'amount': 0,
    }
    data = {
        'file_id': file_id,
    }
    try:
        response = requests.get(
            url=f"{FILE_API_URL}{os.getenv('BOT_TOKEN')}/{file_path}",
            data=data
        )
        if len(response.text) > 0:
            for item in response.text.split('\n'):
                result_item = item.strip().split('|')
                if len(result_item) == 3:
                    result['credentials'].append(result_item)
        result['status'] = 0
        result['amount'] = len(result['credentials'])
    except Exception:
        pass
    return result


@app.task
def validate(scan_id: int, user_id):
    sync_send_message(message=f"Your scan {scan_id}, has been started", chat_id=user_id)
    # Getting data from document
    scan_repo = ScanRepository()
    scan = scan_repo.get_by_id(scan_id=scan_id)[0]
    file_result = get_file_credentials(file_path=scan.file_path, file_id=scan.file_id)
    if file_result['status'] == 0:
        sync_send_message(message=file_result['credentials'], chat_id=user_id)

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
