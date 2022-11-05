from aiogram.dispatcher.webhook import DEFAULT_ROUTE_NAME
from aiogram.utils import executor
from aiogram.utils.executor import set_webhook

from bot import dp, WEBHOOK_PATH, WEBAPP_HOST, WEBAPP_PORT
from entities.db.db_engine import engine
from handlers.admin import register_handlers_admin
from handlers.client import register_handlers_client
from entities.db.db_tables import Base

Base.metadata.create_all(engine)


register_handlers_client(dp)
register_handlers_admin(dp)


if __name__ == '__main__':
    executor = set_webhook(dispatcher=dp,
                           webhook_path=WEBHOOK_PATH,
                           loop=None,
                           skip_updates=None,
                           check_ip=False,
                           retry_after=None,
                           route_name=DEFAULT_ROUTE_NAME,
                           )
    executor.run_app(host=WEBAPP_HOST, port=WEBAPP_PORT)