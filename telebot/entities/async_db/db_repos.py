import datetime

from sqlalchemy.future import select
from sqlalchemy.orm import Session

from entities.async_db.db_specifications import AIOScanSpecification
from entities.async_db.db_tables import Credential, Scan


class AIOCredentialRepo:
    model = Credential

    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def get_all_credentials(self):
        credentials = await self.db_session.execute(select(self.model))
        print('doing_good')
        return credentials.all()


class AIOScanRepo:
    model = Scan

    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def get_with(self, scan_specification: AIOScanSpecification):
        credentials = await self.db_session.execute(
            select(self.model).filter(
                *scan_specification.is_satisfied()
            )
        ).all()
        return credentials
