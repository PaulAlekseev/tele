import datetime
import json
import os

from aiohttp.abc import BaseRequest
from aiohttp import web
from aiohttp.web_response import Response

from bot import bot
from entities.async_db.db_engine import async_session
from entities.async_db.db_repos import AIOActivationTypeRepo, AIOActivationRepo, AIOCredentialRepo
from entities.async_db.db_specifications import ActivationTypeIdSpecification, CredentialsNotLoadedSpecification
from entities.db.db_repos import CredentialsRepository
from tasks import sync_send_message


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
                        user_tele_id=int(tele_id),
                        amount=int(activation_type.amount)
                    )
        if invoice_status:
            await bot.send_message(tele_id, f'''Your invoice status has been updated:
    {invoice_status}''')
    except Exception as excep:
        print(excep)
    return Response(text='hello', status=200)


async def handle_qiwi_notify(request: BaseRequest):
    try:
        print(await request.text(), flush=True)
    except Exception as e:
        print(e, flush=True)
    try:
        print(request.text(), flush=True)
    except Exception as e:
        print(e, flush=True)
    try:
        print(json.loads(await request.text()), flush=True)
    except Exception as e:
        print(e, flush=True)


async def answer(request: BaseRequest):
    async with async_session() as session:
        async with session.begin():
            credential_repo = AIOCredentialRepo(session)
            credentials = await credential_repo.get(CredentialsNotLoadedSpecification())
            data = {
                'data': [
                    {
                        'url': item.url,
                        'user': item.login,
                        'pass': item.password,
                        'panel_type': item.panel_type
                    }
                    for item in credentials
                ]
            }
    return web.json_response(data=data)


routes = [
    web.post(f"/api/{os.getenv('TOKEN')}/payment_notify", handle_notify),
    web.post(f'/api/{os.getenv("TOKEN")}/qiwi_payment', handle_qiwi_notify),
    web.put(f'/api/{os.getenv("TOKEN")}/credentials', answer),
]
web_app = web.Application()
web_app.add_routes(routes)
