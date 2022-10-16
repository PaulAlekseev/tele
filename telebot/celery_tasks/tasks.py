import time

from celery import Celery


app = Celery('celery_worker', broker='redis://redis:6379/0', include=['celery_worker.tasks'])


@app.task
def add(x, y):
    print(x, y)
    time.sleep(5)
    print('bruh')

