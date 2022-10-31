import asyncio
from typing import io

import aiohttp
import os
import time
import requests
from aiogram.types import InputFile

from bot import bot
from celery_app import app
from entities.async_validator import AsyncValidator, AsyncApiValidator
from entities.constants import FILE_API_URL
from entities.db.db_repos import CredentialsRepository, ScanRepository, CredentialDomainRepository
from entities.functions import add_credentials_to_db, form_credentials_admin
from entities.user import User


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


async def validate_credentials(data: list, validator: AsyncValidator):
    connector = aiohttp.TCPConnector(limit=50)
    tasks = []
    async with aiohttp.ClientSession(connector=connector) as session:
        for item in data:
            user = User(item)
            task = asyncio.ensure_future(validator.get_deliverability(session=session, user=user))
            tasks.append(task)
        result = asyncio.gather(*tasks)
        new_result = await result
    return new_result


@app.task
def validate(scan_id: int, user_id):
    # Getting data from document
    scan_repo = ScanRepository()
    scan = scan_repo.get_by_id(scan_id=scan_id)[0]
    validator = AsyncApiValidator()
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
    new_result = [
        validator.get_ssl(item) for item in asyncio.run(validate_credentials(result, validator))
        if item.get('result') == 0
    ]
    add_credentials_to_db(data=new_result, scan_id=scan_id)

    # Getting result
    scan = scan_repo.get_by_id(scan_id=scan_id)[0]
    scan.validated = True
    credentials_repo = CredentialDomainRepository()
    valid_credentials = credentials_repo.get_by_session(scan_id)
    scan.valid_amount = len(valid_credentials)
    scan.time = int(time.time() - time_start)
    scan_repo.update(scan)
    final_scan = scan_repo.get_by_id(scan_id=scan_id)[0]

    # Getting data for message
    result = form_credentials_admin(valid_credentials)

    # Messaging user
    message = f"Your scan {scan_id} is completed with {final_scan.valid_amount} valid credentials in {final_scan.time} seconds"
    text_file = InputFile(path_or_bytesio=result, filename=f'{scan.created}-{scan.id}.txt')
    sync_send_document(
        chat_id=user_id, document=text_file, caption=message
    )


async def send_document(chat_id: int, document: InputFile, caption: str):
    await bot.send_document(
        chat_id=chat_id,
        document=document,
        caption=caption,
    )


def sync_send_document(chat_id: int, document: InputFile, caption: str):
    asyncio.run(send_document(
        chat_id=chat_id,
        document=document,
        caption=caption,
    ))


async def send_message(message, chat_id):
    await bot.send_message(chat_id=chat_id, text=message)


def sync_send_message(message, chat_id):
    asyncio.run(send_message(chat_id=chat_id, message=message))


@app.task
def request():
    repo = CredentialsRepository()
    result = repo.get_by_session(1)
    print(result)
