import datetime

from sqlalchemy.future import select
from sqlalchemy.orm import Session

from entities.async_db.db_specifications import AIOScanSpecification, AIOUserSpecification
from entities.async_db.db_tables import Credential, Scan, User


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

    async def create(self, user_id: int, file_id: str, file_path):
        new_scan = self.model(
            user_id=user_id,
            file_id=file_id,
            file_path=file_path
        )
        scan = await self.db_session.add(new_scan)
        return scan

    async def get_with(self, scan_specification: AIOScanSpecification):
        credentials = await self.db_session.execute(
            select(self.model).filter(
                *scan_specification.is_satisfied()
            )
        )
        return credentials.scalars()


class AIOUserRepository:
    model = User

    def __init__(self, db_session):
        self.db_session = db_session

    async def create(self, user_id: int) -> User:
        new_user = self.model(
            tele_id=user_id
        )
        self.db_session.add(new_user)
        await self.db_session.flush()
        return new_user

    async def get_user(self, user_specification: AIOUserSpecification) -> User:
        user = await self.db_session.execute(
            select(self.model).filter(
                user_specification.is_satisfied()
            )
        )
        return user.all()
