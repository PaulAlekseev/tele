from entities.async_db.db_tables import Activation, User, ActivationType


class Specification:
    def is_satisfied(self):
        pass


class ActivationSpecification(Specification):
    model = Activation


class UserSpecification(Specification):
    model = User


class ActivationTypeSpecification(Specification):
    model = ActivationType


class ActivationUserIdSpecification(ActivationSpecification):
    def __init__(self, user_tele_id):
        self._user_tele_id = user_tele_id

    def is_satisfied(self):
        return self.model.user_tele_id == self._user_tele_id


class ActivationTypeIdSpecification(ActivationTypeSpecification):
    def __init__(self, id):
        self._id = id

    def is_satisfied(self):
        return self.model.id == self._id


class ActivationTypeActiveSpecification(ActivationTypeSpecification):
    def is_satisfied(self):
        return self.model.active == True


class ActivationTypeAllSpecification(ActivationTypeSpecification):
    def is_satisfied(self):
        return self.model.id >= 0
