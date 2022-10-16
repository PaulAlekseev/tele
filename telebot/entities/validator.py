import json
from abc import ABC, abstractmethod

import requests

from entities.constants import VALIDATE_DOMAIN_DATA, DELIVERABILITY_STRING
from entities.deliverability_checker import DeliverabilityChecker
from entities.form_former import FormFormer
from entities.functions import change_credentials_password, get_cert, get_ssl_status, gather_cpanel_domains, \
    gather_whm_domains
from entities.header import Header
from entities.cfg_handler import ConfigHandler
from entities.url_handler import UrlHandler
from entities.user import User


class Validator(ABC):
    def __init__(self):
        self._header = Header()
        self._url_handler = UrlHandler()
        self._timeout = ConfigHandler.get_attributes(
            'timeout'
        )['timeout']
        self._check_ports_on_error = ConfigHandler.get_attributes(
            'check_ports_error'
        )['check_ports_error']
        self._check_ports_on_wrong_credentials = ConfigHandler.get_attributes(
            'check_ports_wrong_credentials'
        )['check_ports_wrong_credentials']
        self._validate_domain_data = VALIDATE_DOMAIN_DATA

    @abstractmethod
    def validate_credentials(self, user: User) -> dict:
        """
        Returns data with additional key: result
        0 - Valid credentials
        1 - Captcha
        2 - Invalid credentials
        """
        pass


class APIValidator(Validator):
    def validate_credentials(self, user: User) -> dict:
        data = user.get_dictionary()
        data['result'] = 2
        for url in self._url_handler.get_allowed_urls(data['url']):
            try:
                response = user.session.post(
                    url=url,
                    data=data['credentials'],
                    headers=self._header.get_header(),
                    timeout=self._timeout
                )
            except Exception:
                if self._check_ports_on_error:
                    continue
                break
            try:
                content = json.loads(response.content.decode('utf-8'))
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

    def get_domains(self, user: User):
        data = self.validate_credentials(user)
        if data.get('result') > 0:
            return data
        try:
            response = user.session.post(
                url=self._url_handler.get_cpanel_domain_url(data.get('url'), user.secret_key),
                data=self._validate_domain_data,
                timeout=self._timeout
            )
            status = 0
        except Exception:
            data['domains'] = None
            return data
        if response.status_code != 200:
            try:
                response = user.session.post(
                    url=self._url_handler.get_whm_domain_url(data.get('url'), user.secret_key),
                    timeout=self._timeout
                )
                status = 1
            except Exception:
                data['domains'] = None
                return data
        try:
            content = json.loads(response.content.decode('utf-8')).get('data')
        except Exception:
            data['domains'] = None
            return data
        result = gather_cpanel_domains(content) if status == 0 else gather_whm_domains(content)
        if result is None:
            data.update({
                'result': 2
            })
            return data
        data['domains'] = {
            item[0]: {'domain': item[0], 'type': item[1], 'ssl_status': 'No info'} for item in result
        }
        return data

    def get_ssl(self, user: User):
        data = self.get_domains(user)
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

    def get_deliverability(self, user: User):
        data = self.get_ssl(user)
        if data.get('result') > 0:
            return data
        if data.get('domains') is None:
            return data
        domains = [item for item in data['domains'].keys()]
        url = f'{data["url"]}{user.secret_key}{DELIVERABILITY_STRING}?{FormFormer.return_full_source(domains)}'
        try:
            response = user.session.post(
                url=url,
                timeout=self._timeout
            )
        except Exception:
            return data
        try:
            content = json.loads(response.content)
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


class SlowValidator(Validator):
    def validate_credentials(self, data: dict) -> dict:
        data['result'] = 2
        for url in self._url_handler.get_allowed_urls(data['url']):
            try:
                response_initial = requests.post(
                    url=url,
                    data=data['credentials'],
                    headers=self._header.get_header(),
                    timeout=self._timeout
                )
            except Exception:
                if self._check_ports_on_error:
                    continue
                break

            try:
                response_changed = requests.post(
                    url=url,
                    data=change_credentials_password(data['credentials']),
                    headers=self._header.get_header(),
                    timeout=self._timeout
                )
            except Exception:
                if self._check_ports_on_error:
                    continue
                break

            if response_changed.status_code != response_initial.status_code:
                data['result'] = 0
                break
            if not self._check_ports_on_wrong_credentials:
                break
        return data


class FastValidator(Validator):
    def validate_credentials(self, data: dict) -> dict:
        data['result'] = 2
        for url in self._url_handler.get_allowed_urls(data['url']):
            try:
                response_initial = requests.post(
                    url=url,
                    data=data['credentials'],
                    headers=self._header.get_header(),
                    timeout=self._timeout
                )
            except Exception:
                if self._check_ports_on_error:
                    continue
                break

            if response_initial.status_code == 200:
                data['result'] = 0
                break
            if not self._check_ports_on_wrong_credentials:
                break
        return data


validators = {
    'Fast': FastValidator(),
    'Slow': SlowValidator(),
    'API': APIValidator()
}
