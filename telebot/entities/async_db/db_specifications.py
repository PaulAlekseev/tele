from abc import ABC
from datetime import date

from entities.async_db.db_tables import Scan, User


class Specification:
    def is_satisfied(self):
        pass


class AIOScanSpecification(Specification):
    model = Scan


class AIOUserSpecification(Specification):
    model = User


class AIOScanDateUserSpecification(AIOScanSpecification):
    def __init__(self, user_id: int, scan_date: date):
        self._user_id = user_id
        self._scan_date = scan_date

    def is_satisfied(self):
        return self.model.user_id == self._user_id, self.model.created == self._scan_date


class AIOUserTeleIdSpecification(AIOUserSpecification):
    def __init__(self, user_tele_id: int):
        self._user_tele_id = user_tele_id

    def is_satisfied(self):
        return self.model.tele_id.__eq__(self._user_tele_id)
