from celery import Celery


app = Celery(
    'tele',
    broker='redis://redis:6379/0',
    include=['tasks', ]
)
