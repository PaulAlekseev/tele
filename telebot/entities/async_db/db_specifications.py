from typing import List

from entities.async_db.db_tables import Activation, User, ActivationType, Credential


class Specification:
    def is_satisfied(self):
        pass


class ActivationSpecification(Specification):
    model = Activation


class UserSpecification(Specification):
    model = User


class CredentialsSpecification(Specification):
    model =Credential


class ActivationTypeSpecification(Specification):
    model = ActivationType


class CredentialsIdsInSpecification(CredentialsSpecification):
    def __init__(self, ids:List[int]):
        self._ids = ids

    def is_satisfied(self):
        return self.model.id in self._ids,


class ActivationUserIdSpecification(ActivationSpecification):
    def __init__(self, user_tele_id):
        self._user_tele_id = user_tele_id

    def is_satisfied(self):
        return self.model.user_tele_id == self._user_tele_id


class CredentialsNotLoadedSpecification(CredentialsSpecification):
    def is_satisfied(self):
        return self.model.loaded == False,


class ActivationTypeIdSpecification(ActivationTypeSpecification):
    def __init__(self, _id: int):
        self._id = _id

    def is_satisfied(self):
        return self.model.id.__eq__(self._id),


class ActivationTypeActiveSpecification(ActivationTypeSpecification):
    def is_satisfied(self):
        return self.model.active.is_(True),


class ActivationTypeAllSpecification(ActivationTypeSpecification):
    def is_satisfied(self):
        return self.model.id >= 0,
