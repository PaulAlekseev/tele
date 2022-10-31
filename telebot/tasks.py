import asyncio
import aiohttp
import os
import time
from concurrent.futures import ThreadPoolExecutor

import requests

from bot import bot
from celery_app import app
from entities.async_validator import AsyncValidator, AsyncApiValidator
from entities.constants import FILE_API_URL
from entities.db.db_repos import CredentialsRepository, ScanRepository
from entities.user import User
from entities.validator import APIValidator


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
                    result['credentials'].append({
                        'url': result_item[0],
                        'credentials': {
                            'user': result_item[1],
                            'pass': result_item[2],
                        }
                    })
        result['status'] = 0
        result['amount'] = len(result['credentials'])
    except Exception:
        pass
    return result


async def validate_credentials(data: list) -> tuple:
    connector = aiohttp.TCPConnector(limit=50)
    validator = AsyncApiValidator()
    tasks = []
    async with aiohttp.ClientSession(connector=connector) as session:
        for item in data:
            user = User(item)
            task = asyncio.ensure_future(validator.get_deliverability(session=session, user=user))
            tasks.append(task)
        result = asyncio.gather(*tasks)
    return await result


@app.task
def validate(scan_id: int, user_id):
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

    # Scanning for data
    time_start = time.time()
    new_result = asyncio.run(validate_credentials(result))
    print(new_result)


    # with ThreadPoolExecutor(max_workers=cpu_count - 2 if cpu_count > 3 else cpu_count) as executor:
    #     for item in result:
    #         executor.submit(
    #             validate_credentials,
    #             data=item,
    #             scan_id=scan_id,
    #             validator=APIValidator()
    #         )
    #     sync_send_message(message=f"Your scan {scan_id}, has been started", chat_id=user_id)
    #     executor.shutdown(wait=True)
    #
    # # Getting result
    # scan = scan_repo.get_by_id(scan_id=scan_id)[0]
    # scan.validated = True
    # credentials_repo = CredentialsRepository()
    # valid_credentials = credentials_repo.get_by_session(scan_id)
    # scan.valid_amount = len(valid_credentials)
    # scan.time = int(time.time() - time_start)
    # scan_repo.update(scan)
    # final_scan = scan_repo.get_by_id(scan_id=scan_id)[0]
    #
    # # Getting data for message
    # result = ''.join([f"{item.url}|{item.login}|{item.password}" for item in valid_credentials])
    #
    # # Messaging user
    # sync_send_message(message=f"Your scan {scan_id} is completed with {final_scan.valid_amount} valid credentials in {final_scan.time} seconds", chat_id=user_id)


async def send_message(message, chat_id):
    await bot.send_message(chat_id=chat_id, text=message)


def sync_send_message(message, chat_id):
    asyncio.run(send_message(chat_id=chat_id, message=message))


@app.task
def request():
    repo = CredentialsRepository()
    result = repo.get_by_session(1)
    print(result)
