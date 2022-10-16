import time

from celery import Celery


app = Celery('celery_worker', broker='redis://redis:6379/0')


@app.task(bind=True)
def add():
    time.sleep(5)
    print('bruh')

