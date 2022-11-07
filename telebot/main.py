from aiogram.utils.executor import set_webhook, start_webhook, start_polling

from bot import dp, WEBHOOK_PATH, WEBAPP_HOST, WEBAPP_PORT, bot, WEBHOOK_URL
from entities.db.db_engine import engine
from handlers.admin import register_handlers_admin
from handlers.client import register_handlers_client
from entities.db.db_tables import Base

Base.metadata.create_all(engine)


register_handlers_client(dp)
register_handlers_admin(dp)


async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)
    # insert code here to run it after start


async def on_shutdown(dp):
    # Remove webhook (not acceptable in some cases)
    await bot.delete_webhook()

    # Close DB connection (if used)
    await dp.storage.close()
    await dp.storage.wait_closed()


executor = set_webhook(dispatcher=dp,
                       webhook_path=WEBHOOK_PATH,
                       loop=None,
                       skip_updates=None,
                       check_ip=False,
                       on_startup=on_startup,
                       on_shutdown=on_shutdown,
                       retry_after=None,
                       route_name=DEFAULT_ROUTE_NAME,
                       )
executor.run_app(host=WEBAPP_HOST, port=WEBAPP_PORT)

# start_webhook(
#     dispatcher=dp,
#     webhook_path=WEBHOOK_PATH,
#     on_startup=on_startup,
#     on_shutdown=on_shutdown,
#     skip_updates=True,
#     host=WEBAPP_HOST,
#     port=WEBAPP_PORT,
# )
# start_polling(dispatcher=dp, skip_updates=True)