import os

import requests

from celery import Celery
from other.constants import IDS

app = Celery(
    'tele',
    broker='redis://redis:6379/0',
    include=['tasks', ]
)


