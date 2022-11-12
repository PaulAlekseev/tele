import requests
from entities.constants import URL_LOGIN_STRING


class User:
    def __init__(self, data):
        self.session = requests.session()
        self.credentials = data.get('credentials')
        self.url = data.get('url')
        self.region = data.get('region')
        self.secret_key = None

    def authenticate(self):
        url = (''.join([self.url, URL_LOGIN_STRING]))
        try:
            result = self.session.post(url, data=self.credentials)
        except Exception:
            return False
        result_json = result.json()
        print(result_json)
        self.secret_key = result_json.get('security_token')
        print(self.secret_key)
        return True if result_json.get('status') == 1 else False

    def get_dictionary(self):
        return {
            'url': self.url,
            'credentials': self.credentials,
            'region': self.region
        }