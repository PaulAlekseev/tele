from entities.constants import URL_LOGIN_STRING, URL_DOMAIN_STRING, WHM_DOMAIN_STRING, ALLOWED_PORTS


class UrlHandler:
    def __init__(self):
        self._allowed_ports = ALLOWED_PORTS
        self._url_login_string = URL_LOGIN_STRING
        self._url_domain_string = URL_DOMAIN_STRING
        self._url_whm_domain_string = WHM_DOMAIN_STRING

    def get_allowed_urls(self, url: str) -> list:
        url_without_port = url.split(':')[0:-1]
        return [
            ':'.join(url_without_port + [port]) + self._url_login_string for port in self._get_ports(url)
        ]

    def _get_ports(self, url):
        current_port = url.split(':')[-1]
        for item in self._allowed_ports:
            if current_port in item:
                result = list(item)
                result.insert(0, result.pop(result.index(current_port)))
                return result
        return [current_port]

    def get_cpanel_domain_url(self, url:str, secret_key: str) -> str:
        return ''.join((url, secret_key, self._url_domain_string))

    def get_whm_domain_url(self, url:str, secret_key: str) -> str:
        return ''.join((url, secret_key, self._url_whm_domain_string))
