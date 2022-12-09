import os

import requests

from celery import Celery
from other.constants import IDS
from tasks import sync_send_message

app = Celery(
    'tele',
    broker='redis://redis:6379/0',
    include=['tasks', ]
)


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
