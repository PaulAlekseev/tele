from time import sleep

import fake_useragent


class Header:
    def __init__(self):
        self._header = None
        self._update_header()

    def _update_header(self):
        try:
            self._header = {
                'user-agent': 'Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5355d Safari/8536.25',
            }
        except Exception:
            sleep(3)
            self._update_header()

    def get_header(self):
        return self._header
