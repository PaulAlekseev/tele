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
            'notify_url': f"{WEBHOOK_HOST}/api/{os.getenv('TOKEN')}/payment_notify",
            'custom_data1': tele_id,
            'custom_data2': custom_data
        }
        self._headers = {
            'Accept': 'application/json',
        }
        self._session = session
        self._response = None

    async def create_invoice(self, ):
        async with self._session.post(
                url=self._url, data=self._body, headers=self._headers
        ) as response:
            result = json.loads(await response.text())
            self._response = result
            return self._response

    async def get_address(self):
        return self._response['data']['address']

    async def get_url(self):
        return self._response
