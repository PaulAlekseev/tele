from typing import List

import sqlalchemy
from sqlalchemy import desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from entities.async_db.db_specifications import ActivationSpecification, UserSpecification, ActivationTypeSpecification, \
    CredentialsSpecification
from entities.async_db.db_tables import Credential, Activation, Domain, User, ActivationType, Invoice


class AIOCredentialRepo:
    model = Credential

    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def get_all_credentials(self):
        credentials = await self.db_session.execute(select(self.model))
        return credentials.all()

    async def get(self, credential_specification: CredentialsSpecification) -> List[Credential]:
        credentials = await self.db_session.execute(
            select(self.model).filter(
                *credential_specification.is_satisfied()
            )
        )
        return credentials.scalars().all()

    async def update(self, credentials: Credential) -> Credential:
        self.db_session.add(credentials)
        await self.db_session.commit()
        return credentials


class AIOActivationRepo:
    model = Activation

    def __init__(self, db_session):
        self.db_session = db_session

    async def create(
            self,
            expiration_date,
            user_tele_id: str,
            amount_daily: int,
            amount_month: int,
            amount_once: int,
    ):
        new_activation = self.model(
            expires=expiration_date,
            user_tele_id=user_tele_id,
            amount_daily=amount_daily,
            amount_check=amount_daily,
            amount_month=amount_month,
            amount_once=amount_once
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

    async def get_latest(self, user_tele_id: str) -> Activation:
        activation = await self.db_session.execute(
            select(self.model).filter(
                self.model.user_tele_id == user_tele_id
            ).order_by(desc(self.model.expires))
        )
        return activation.scalars().first()

    async def update(self, activation: Activation) -> Activation:
        self.db_session.add(activation)
        await self.db_session.flush()
        return activation


class AIOCredentialDomainRepo:
    model1 = Credential
    model2 = Domain

    def __init__(self, session):
        self._session = session

    async def get_by(self, credentials):
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
                'path': item.path,
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

    async def get_by_date_range(self, date1, date2):
        credentials = await self._session.execute(
            select(self.model1).filter(
                self.model1.created >= date1,
                self.model1.created <= date2
            )
        )
        return await self.get_by(credentials)

    # async def get_by_region(self, region):
    #     credentials = await self._session.execute(
    #         select(self.model1).filter(
    #             self.model1.region == region
    #         )
    #     )
    #     return await self.get_by(credentials)


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

    async def get(self, user_specification: UserSpecification):
        users = await self.db_session.execute(
            select(self.model).filter(
                *user_specification.is_satisfied()
            )
        )
        return users.scalars().all()


class AIOActivationTypeRepo:
    model = ActivationType

    def __init__(self, session):
        self.db_session = session

    async def create(
            self,
            name: str,
            amount_once: str,
            amount_daily: str,
            amount_month: str,
            price: str,
    ):
        new_activation_type = self.model(
            name=name,
            amount_once=amount_once,
            amount_month=amount_month,
            amount_daily=amount_daily,
            active=True,
            price=price
        )
        self.db_session.add(new_activation_type)
        await self.db_session.flush()
        return new_activation_type

    async def get(self, activation_type_specification: ActivationTypeSpecification) -> List[ActivationType]:
        activation_types = await self.db_session.execute(
            select(self.model).filter(
                *activation_type_specification.is_satisfied()
            )
        )
        return activation_types.scalars().all()

    async def update(self, activation_type: ActivationType):
        self.db_session.add(activation_type)
        await self.db_session.flush()
        return activation_type


class AIOInvoiceRepo:
    model = Invoice

    def __init__(self, session: AsyncSession):
        self._db_session = session

    async def create(self, invoice: Invoice) -> Invoice:
        try:
            new_invoice = await self._db_session.execute(select(self.model).filter(
                self.model.unique_id == invoice.unique_id,
            ))
            new_invoice = new_invoice.one()
        except sqlalchemy.orm.exc.NoResultFound:
            new_invoice = invoice
            self._db_session.add(new_invoice)
            await self._db_session.flush()
        return new_invoice
