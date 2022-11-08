import os

from aiohttp.abc import BaseRequest
from aiohttp import web
from aiohttp.web_response import Response

from bot import bot


async def handle_notify(request: BaseRequest):
    post = await request.post()
    invoice_status = post.get('status')
    tele_id = post.get('custom_data1')
    custom_data = post.get('custom_data2')
    if invoice_status == 'paid':
    if invoice_status:
        await bot.send_message(tele_id, f'''Your invoice status has been updated:
{invoice_status}''')
    return Response(text='hello', status=200)


routes = [
    web.post(f"/api/{os.getenv('TOKEN')}/payment_notify", handle_notify)
]
app = web.Application()
app.add_routes(routes)