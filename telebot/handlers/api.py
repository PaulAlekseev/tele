import datetime
import os

from aiogram.types import callback_query
from aiohttp.abc import BaseRequest
from aiohttp import web
from aiohttp.web_response import Response

from bot import bot
from entities.async_db.db_engine import async_session
from entities.async_db.db_repos import AIOActivationTypeRepo, AIOActivationRepo
from entities.async_db.db_specifications import ActivationTypeIdSpecification


async def handle_notify(request: BaseRequest):
    try:
        post = await request.post()
        invoice_status = post.get('status')
        tele_id = post.get('custom_data1')
        custom_data = post.get('custom_data2')
        if invoice_status == 'Paid':
            async with async_session() as session:
                async with session.begin():
                    activation_type_repo = AIOActivationTypeRepo(session)
                    activation_repo = AIOActivationRepo(session)
                    activation_types = await activation_type_repo.get(
                        ActivationTypeIdSpecification(int(custom_data))
                    )
                    activation_type = activation_types[0]
                    activation = await activation_repo.create(
                        expiration_date=datetime.date.today() + datetime.timedelta(days=30),
                        user_tele_id=callback_query.from_user.id,
                        amount=activation_type.amount
                    )
        await bot.send_message(callback_query.from_user.id, text=activation_text[callback_query.data])
        if invoice_status:
            await bot.send_message(tele_id, f'''Your invoice status has been updated:
    {invoice_status}''')
    except Exception:
        pass
    return Response(text='hello', status=200)


routes = [
    web.post(f"/api/{os.getenv('TOKEN')}/payment_notify", handle_notify)
]
web_app = web.Application()
web_app.add_routes(routes)
