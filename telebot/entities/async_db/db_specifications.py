from abc import ABC
from datetime import date

from entities.async_db.db_tables import Scan


class Specification:
    def is_satisfied(self):
        pass


class AIOScanSpecification(Specification):
    model = Scan


class AIOScanDateUserSpecification(AIOScanSpecification):
    def __init__(self, user_id: int, scan_date: date):
        self._user_id = user_id
        self._scan_date = scan_date

    def is_satisfied(self):
        return self.model.user_id == self._user_id, self.model.created == self._scan_date
