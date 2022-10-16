from time import sleep

import fake_useragent


class Header:
    def __init__(self):
        self._header = None
        self._update_header()

    def _update_header(self):
        try:
            self._header = {
                'user-agent': fake_useragent.UserAgent().google,
            }
        except Exception:
            sleep(3)
            self._update_header()

    def get_header(self):
        return self._header
