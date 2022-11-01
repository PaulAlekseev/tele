from datetime import date

from entities.async_db.db_tables import Activation


class Specification:
    def is_satisfied(self):
        pass


class ActivationSpecification(Specification):
    model = Activation


class ActivationUserIdSpecification(ActivationSpecification):
    def __init__(self, user_tele_id):
        self._user_tele_id = user_tele_id

    def is_satisfied(self):
        return self.model.user_tele_id == self._user_tele_id
