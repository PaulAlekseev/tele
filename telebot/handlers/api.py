import os

from aiohttp.abc import BaseRequest
from aiohttp import web
from aiohttp.web_response import Response

from bot import bot


async def handle_notify(request: BaseRequest):
    try:
        post = await request.post()
        invoice_status = post.get('status')
        tele_id = post.get('custom_data1')
        custom_data = post.get('custom_data2')
        if invoice_status == 'paid':
            await bot.send_message(
                chat_id=tele_id,
                text='paid lol'
            )
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
