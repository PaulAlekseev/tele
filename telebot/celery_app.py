from celery import Celery
from tasks import check_other

app = Celery(
    'tele',
    broker='redis://redis:6379/0',
    include=['tasks', ]
)


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(60, check_other.s(), expires=15)
