import asyncio
import multiprocessing
import os
import time
from concurrent.futures import ThreadPoolExecutor

import requests

from bot import bot
from celery_app import app
from entities.constants import FILE_API_URL
from entities.db.db_repos import CredentialsRepository, ScanRepository
from entities.functions import validate_credentials
from entities.validator import APIValidator


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
    if file_result['status'] > 1:
        sync_send_message(message="Sorry, we couldn't find your file", chat_id=user_id)
        scan.validated = True
        scan_repo.update(scan)
        return 0
    else:
        result = file_result['credentials']
    sync_send_message(message=f"Scanning started", chat_id=user_id)

    # Scanning for data
    cpu_count = multiprocessing.cpu_count()
    time_start = time.time()
    with ThreadPoolExecutor(max_workers=cpu_count - 2 if cpu_count > 3 else cpu_count) as executor:
        for item in result:
            executor.submit(
                validate_credentials,
                data=item,
                scan_id=scan_id,
                validator=APIValidator()
            )

    sync_send_message(message=f"Last thing", chat_id=user_id)
    # Getting result
    scan = scan_repo.get_by_id(scan_id=scan_id)[0]
    scan.validated = True
    credentials_repo = CredentialsRepository()
    scan.valid_amount = len(credentials_repo.get_by_session(scan_id))
    scan.time = int(time.time() - time_start)
    scan_repo.update(scan)
    final_scan = scan_repo.get_by_id(scan_id=scan_id)[0]

    # Messaging user
    sync_send_message(message=f"Your scan {scan_id} is completed with {final_scan.valid_amount} valid credentials and in {final_scan.time} seconds", chat_id=user_id)



async def send_message(message, chat_id):
    await bot.send_message(chat_id=chat_id, text=message)


def sync_send_message(message, chat_id):
    asyncio.run(send_message(chat_id=chat_id, message=message))


@app.task
def request():
    repo = CredentialsRepository()
    result = repo.get_by_session(1)
    print(result)
