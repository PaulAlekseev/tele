import os

from entities.constants import CONFIG_PATH
import json


class ConfigHandler:

    @staticmethod
    def _check_exists():
        if os.path.exists(CONFIG_PATH):
            return True
        return False

    @staticmethod
    def get_attributes(*args):
        with open(CONFIG_PATH) as file:
            try:
                data = json.load(file)
            except Exception:
                data = {}
            result = {arg: value for arg, value in data.items() if arg in args}
        return result

    @staticmethod
    def set_attributes(**kwargs):
        with open(CONFIG_PATH) as file:
            try:
                data = json.load(file)
            except Exception:
                data = {}

        data.update(kwargs)
        with open(CONFIG_PATH) as file:
            json.dump(data, file)
        return data
