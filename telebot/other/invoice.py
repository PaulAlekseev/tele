import datetime
import json
import os

import aiohttp

from bot import WEBHOOK_HOST


class Invoice:
    def __init__(
            self,
            amount: str,
            session: aiohttp.ClientSession,
            token_name: str,
            tele_id: str,
            custom_data: str,
            api_key: str,
            password: str,
    ):
        self._url = f'https://coinremitter.com/api/v3/{token_name}/create-invoice'
        self._body = {
            'api_key': api_key,
            'password': password,
            'currency': 'USD',
            'amount': amount,
            'notify_url': f"{WEBHOOK_HOST}api/{os.getenv('TOKEN')}/payment_notify",
            'custom_data1': tele_id,
            'custom_data2': custom_data
        }
        self._headers = {
            'Accept': 'application/json',
        }
        self._session = session
        self._response = None

    async def create_invoice(self):
        async with self._session.post(
                url=self._url, data=self._body, headers=self._headers
        ) as response:
            result = json.loads(await response.text())
            self._response = result
            return self._response

    async def get_address(self):
        return self._response['data']['address']

    async def get_url(self):
        return self._response['data']['url']


class QiwiInvoice:
    def __init__(
            self,
            user_tele_id: int,
            price: int,
            expiration_hours: int,
            comment: str,
            session: aiohttp.ClientSession
    ):
        self.url = f'https://api.qiwi.com/partner/bill/v1/bills/{user_tele_id}'
        self.session = session
        self.headers = {
            'content-type': 'application/json',
            'accept': 'application/json',
            'Authorization': f'Bearer {os.getenv("QIWI_KEY")}'
        }
        date_today = datetime.datetime.today() + datetime.timedelta(hours=expiration_hours)
        self.data = {
            'amount': {
                'currency': 'RUB',
                'value': str(price)
            },
            'comment': comment,
            'expirationDateTime': str(date_today.date()) + 'T' + str(str(date_today.time()).split('.')[0] + '+03:00')
        }

    async def create_invoice(self):
        async with self.session.put(
            url=self.url,
            json=self.data,
            headers=self.headers
        ) as response:
            result = json.loads(await response.text())
            return result
