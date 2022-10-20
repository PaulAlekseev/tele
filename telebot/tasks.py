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
        scan_id = scan_repo.create().id
        repo.add_or_update(
            url=result.get('url'),
            login=result['credentials']['user'],
            password=result['credentials']['pass'],
            scan_id=scan_id,
        )
    sync_send_message(user_id, message_splited[0] + ' done!')


async def send_message(message, user_id):
    await bot.send_message(user_id, message)


def sync_send_message(message, id):
    asyncio.run(send_message(message, id))


@app.task
def request():
    repo = CredentialsRepository()
    result = repo.get_by_session(1)
    print(result)
