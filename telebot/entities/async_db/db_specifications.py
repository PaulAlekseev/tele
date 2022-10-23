from datetime import date

from entities.async_db.db_tables import Scan, User


class Specification:
    def is_satisfied(self):
        pass


class ScanSpecification(Specification):
    model = Scan


class UserSpecification(Specification):
    model = User


class ScanIdSpecification(ScanSpecification):
    def __init__(self, scan_id: int):
        self._scan_id = scan_id

    def is_satisfied(self):
        return self.model.id == self._scan_id


class ScanDateUserSpecification(ScanSpecification):
    def __init__(self, user_id: int, scan_date: date):
        self._user_id = user_id
        self._scan_date = scan_date

    def is_satisfied(self):
        return self.model.user_id == self._user_id, self.model.created == self._scan_date


class UserTeleIdSpecification(UserSpecification):
    def __init__(self, user_tele_id: int):
        self._user_tele_id = user_tele_id

    def is_satisfied(self):
        return self.model.tele_id.__eq__(self._user_tele_id)


class UserDateSpecification(UserSpecification):
    def __init__(self, _date: date):
        self._date = _date

    def is_satisfied(self):
        return self.model.created.__eq__(self._date)
