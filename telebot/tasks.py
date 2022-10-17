import time

from celery_app import app
from entities.db.db_repos import CredentialsRepository
from entities.user import User
from entities.validator import APIValidator


@app.task
def add(message: str):
    print(message.split())
    time.sleep(5)
    print('bruh')


@app.task
def validate(message: str):
    repo = CredentialsRepository()
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
        repo.add_or_update(
            url=result.get('url'),
            login=result['credentials']['user'],
            password=result['credentials']['pass'],
            scan_id=1,
        )
        print('bruh')


@app.task
def request():
    repo = CredentialsRepository()
    result = repo.get_by_session(1)
    print(result)

