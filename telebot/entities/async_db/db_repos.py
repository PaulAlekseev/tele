from typing import List

import sqlalchemy
from sqlalchemy import desc
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from entities.async_db.db_specifications import ActivationSpecification
from entities.async_db.db_tables import Credential, Activation, Domain, User


class AIOCredentialRepo:
    model = Credential

    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def get_all_credentials(self):
        credentials = await self.db_session.execute(select(self.model))
        return credentials.all()


class AIOActivationRepo:
    model = Activation

    def __init__(self, db_session):
        self.db_session = db_session

    async def create(self, expiration_date, user_tele_id):
        new_activation = self.model(
            expires=expiration_date,
            user_tele_id=user_tele_id
        )
        self.db_session.add(new_activation)
        await self.db_session.flush()
        return new_activation

    async def get(self, activation_specification: ActivationSpecification) -> List[Activation]:
        activation = await self.db_session.execute(
            select(self.model).filter(
                *activation_specification.is_satisfied()
            )
        )
        return activation.scalars().all()

    async def get_latest(self, user_tele_id) -> Activation:
        activation = await self.db_session.execute(
            select(self.model).filter(
                self.model.user_tele_id == user_tele_id
            ).order_by(desc(self.model.expires))
        )
        return activation.scalars().first()


class AIOCredentialDomainRepo:
    model1 = Credential
    model2 = Domain

    def __init__(self, session):
        self._session = session

    async def get_by_date_range(self, date1, date2):
        credentials = await self._session.execute(
            select(self.model1).filter(
                self.model1.created >= date1,
                self.model1.created <= date2
            )
        )
        credential_result = credentials.scalars().all()
        credential_ids = [item.id for item in credential_result]
        domains = await self._session.execute(
            select(self.model2).filter(
                self.model2.credential_id.in_(credential_ids)
            )
        )
        domain_result = domains.scalars().all()
        result = {
            str(item.id): {
                'url': item.url,
                'credentials': {
                    'user': item.login,
                    'pass': item.password
                },
                'domains': {

                }} for item in credential_result
        }
        if domain_result:
            for item in domain_result:
                result[str(item.credential_id)]['domains'].update({
                    item.domain: {
                        'domain': item.domain,
                        'type': item.type,
                        'ssl_status': item.status,
                        'email': item.email,
                        'dns_email': item.email_dns,
                    }
                })
        return [item for item in result.values()]


class AIOUserRepo:
    model = User

    def __init__(self, session):
        self.db_session = session

    async def create(self, tele_id):
        try:
            new_user = await self.db_session.execute(select(self.model).filter(
                self.model.tele_id == tele_id,
            ))
            new_user = new_user.one()
        except sqlalchemy.orm.exc.NoResultFound:
            new_user = self.model(
                tele_id=tele_id
            )
            self.db_session.add(new_user)
            await self.db_session.flush()
        return new_user

    async def get_all(self) -> List[User]:
        users = await self.db_session.execute(select(self.model))
        return users.scalars().all()
