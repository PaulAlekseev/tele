import datetime

from sqlalchemy.future import select
from sqlalchemy.orm import Session

from entities.async_db.db_specifications import AIOScanSpecification
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

    async def create(self, user_id: int, file_id: str, file_path: str) -> Scan:
        new_scan = self.model(
            user_id=user_id,
            file_id=file_id,
            file_path=file_path
        )
        scan = self.db_session.add(new_scan)
        await self.db_session.flush()
        return scan

    async def get_with(self, scan_specification: AIOScanSpecification):
        credentials = await self.db_session.execute(
            select(self.model).filter(
                *scan_specification.is_satisfied()
            )
        )
        return credentials.scalars().all()


class AIOUserRepository:
    model = User

    def __init__(self, db_session):
        self.db_session = db_session

    async def create(self, user_id: int) -> User:
        new_user = self.model(
            tele_id=user_id
        )
        user = self.db_session.add(new_user)
        await self.db_session.flush()
        return user
