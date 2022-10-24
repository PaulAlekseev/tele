from sqlalchemy.future import select
from sqlalchemy.orm import Session

from entities.async_db.db_specifications import ScanSpecification
from entities.async_db.db_tables import Credential, Scan


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
