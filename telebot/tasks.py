import time

from celery_app import app


@app.task
def add(message: str):
    print(message.split())
    time.sleep(5)
    print('bruh')
