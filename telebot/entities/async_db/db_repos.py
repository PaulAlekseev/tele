import datetime

from sqlalchemy.future import select
from sqlalchemy.orm import Session

from entities.async_db.db_tables import Credential, Scan


class AIOCredentialRepo:
    model = Credential

    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def get_all_credentials(self):
        credentials = await self.db_session.execute(select(self.model))
        return credentials.all()

    async def get_by_date(self, date: datetime.date):
        credentials = await self.db_session.execute(select(self.model).filter(
            self.model.updated == date
        ))
        return credentials.all()


class AIOScanRepo:
    model = Scan

    def __init__(self, db_session: Session):
        self.db_session
