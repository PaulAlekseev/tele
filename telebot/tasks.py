import time

from celery_app import app
from entities.user import User
from entities.validator import APIValidator


@app.task
def add(message: str):
    print(message.split())
    time.sleep(5)
    print('bruh')


@app.task
def validate(message: str):
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
    print(validator.get_deliverability(user))
