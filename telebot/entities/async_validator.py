import json
from abc import ABC, abstractmethod

from entities.constants import DELIVERABILITY_STRING, TIMEOUT, CHECK_PORTS_ERROR, CHECK_PORTS_WRONG_CREDENTIALS, \
    VALIDATE_DOMAIN_DATA
from entities.deliverability_checker import DeliverabilityChecker
from entities.form_former import FormFormer
from entities.functions import gather_cpanel_domains, gather_whm_domains, get_cert, get_ssl_status
from entities.header import Header
from entities.url_handler import UrlHandler
from entities.user import User


class AsyncValidator(ABC):
    def __init__(self, proxy: str):
        self._header = Header()
        self._url_handler = UrlHandler()
        self._timeout = TIMEOUT
        self._check_ports_on_error = CHECK_PORTS_ERROR
        self._check_ports_on_wrong_credentials = CHECK_PORTS_WRONG_CREDENTIALS
        self._validate_domain_data = VALIDATE_DOMAIN_DATA
        self._proxy = proxy

    @abstractmethod
    def validate_credentials(self, user: User, session) -> dict:
        """
        Returns data with additional key: result
        0 - Valid credentials
        1 - Captcha
        2 - Invalid credentials
        """
        pass

    @abstractmethod
    def get_domains(self, user: User, session):
        pass

    @abstractmethod
    def get_ssl(self, data: dict) -> dict:
        pass

    @abstractmethod
    def get_deliverability(self, user: User, session):
        pass


class AsyncApiValidator(AsyncValidator):
    async def validate_credentials(self, user: User, session) -> dict:
        data = user.get_dictionary()
        data['result'] = 2
        for url in self._url_handler.get_allowed_urls(data['url']):
            try:
                async with session.post(
                    url=url,
                    data=data['credentials'],
                    headers=self._header.get_header(),
                    timeout=self._timeout,
                    proxy=self._proxy
                ) as response:
                    result_content = await response.text()
            except Exception:
                if self._check_ports_on_error:
                    continue
                break
            try:
                content = json.loads(result_content)
            except Exception:
                data['result'] = 1
                break
            user.secret_key = content.get('security_token')
            status = content.get('status')
            if status:
                if status == 1:
                    data['url'] = '/'.join(url.split('/')[0:-2])
                    data['result'] = 0
                    break
                else:
                    data['result'] = 2
                    if self._check_ports_on_wrong_credentials:
                        continue
        return data

    async def get_domains(self, user: User, session):
        data = await self.validate_credentials(user, session)
        if data.get('result') > 0:
            return data
        try:
            async with session.post(
                url=self._url_handler.get_cpanel_domain_url(data.get('url'), user.secret_key),
                data=self._validate_domain_data,
                timeout=self._timeout,
                proxy=self._proxy
            ) as response:
                status = 0
                result = await response.text()
                status_code = response.status
        except Exception as err:
            data['domains'] = None
            return data
        if status_code != 200:
            try:
                async with session.post(
                    url=self._url_handler.get_whm_domain_url(data.get('url'), user.secret_key),
                    timeout=self._timeout
                ) as response:
                    result = await response
                    status = 1
            except Exception:
                data['domains'] = None
                return data
        try:
            content = json.loads(result).get('data')
        except Exception:
            data['domains'] = None
            return data
        result = gather_cpanel_domains(content) if status == 0 else gather_whm_domains(content)
        if result is None:
            data['domains'] = None
            return data
        data['domains'] = {
            item[0]: {'domain': item[0], 'type': item[1], 'ssl_status': 'No info'} for item in result
        }
        return data

    def get_ssl(self, data: dict) -> dict:
        if data.get('result') > 0:
            return data
        if data.get('domains') is None:
            return data
        for domain in data.get('domains').keys():
            cert = get_cert(domain)
            if cert:
                data['domains'][domain].update({
                    'ssl_status': get_ssl_status(cert), 'valid_until': str(cert.not_valid_after.date())
                })
            else:
                data['domains'][domain].update({
                    'ssl_status': 'Not Valid'
                })
        return data

    async def get_deliverability(self, user: User, session):
        data = await self.get_domains(user, session)
        if data.get('result') > 0:
            return data
        if data.get('domains') is None:
            return data
        domains = [item for item in data['domains'].keys()]
        url = f'{data["url"]}{user.secret_key}{DELIVERABILITY_STRING}?{FormFormer.return_full_source(domains)}'
        try:
            async with session.post(
                url=url,
                timeout=self._timeout,
                proxy=self._proxy
            ) as response:
                result = await response.text()
        except Exception:
            return data
        try:
            content = json.loads(result)
        except Exception:
            return data
        deliverability = DeliverabilityChecker.check_deliverability(content)
        for domain, value in data['domains'].items():
            new_value = deliverability.get(domain)
            if new_value:
                data['domains'][domain].update({
                    'email': True if new_value['result'] == 3 else False,
                    'dns_email': True if new_value['local_authority'] == 1 else False
                })
        return data
