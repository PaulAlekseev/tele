import asyncio
import time

from bot import bot
from celery_app import app
from entities.db.db_repos import CredentialsRepository, ScanRepository
from entities.user import User
from entities.validator import APIValidator


@app.task
def add(message: str):
    print(message.split())
    time.sleep(5)
    print('bruh')


@app.task
def validate(message: str, user_id):
    repo = CredentialsRepository()
    scan_repo = ScanRepository()
    message_splited = message.split('|')
    credentials = {
        'url': message_splited[0],
        'credentials': {
            'user': message_splited[1],
            'pass': message_splited[2],
        }
    }
    user = User(credentials)
    validator = APIValidator()
    result = validator.get_deliverability(user)
    if result.get('result') == 0:
        scan_id = scan_repo.get_by_user_id(user)
        repo.add_or_update(
            url=result.get('url'),
            login=result['credentials']['user'],
            password=result['credentials']['pass'],
            scan_id=scan_id,
        )
    sync_send_message(message=message_splited[0] + ' done!', chat_id=user_id)


async def send_message(message, chat_id):
    await bot.send_message(chat_id=chat_id, text=message)


def sync_send_message(message, chat_id):
    asyncio.run(send_message(chat_id=chat_id, message=message))


@app.task
def request():
    repo = CredentialsRepository()
    result = repo.get_by_session(1)
    print(result)
