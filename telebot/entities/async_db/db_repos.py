from typing import List

from sqlalchemy import desc
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from entities.async_db.db_specifications import ScanSpecification, ActivationSpecification
from entities.async_db.db_tables import Credential, Scan, Activation


class AIOCredentialRepo:
    model = Credential

    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def get_all_credentials(self):
        credentials = await self.db_session.execute(select(self.model))
        return credentials.all()


class AIOScanRepo:
    model = Scan

    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def create(self, user_tele_id: int, file_id: str, file_path: str) -> Scan:
        new_scan = self.model(
            user_tele_id=user_tele_id,
            file_id=file_id,
            file_path=file_path
        )
        self.db_session.add(new_scan)
        await self.db_session.flush()
        return new_scan

    async def get_with(self, scan_specification: ScanSpecification):
        credentials = await self.db_session.execute(
            select(self.model).filter(
                *scan_specification.is_satisfied()
            )
        )
        return credentials.scalars().all()


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
            )
        )
        return activation.order_by(desc(self.model.expires)).scalars().first()
