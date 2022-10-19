from sqlalchemy.future import select
from sqlalchemy.orm import Session

from entities.async_db.db_tables import Credential


class AIOCredentialRepo:
    model = Credential

    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def get_all_credentials(self):
        credentials = await self.db_session.execute(select(self.model))
        return credentials.all()

    # async def get_last_scan(self):
    #     credentials = await self.db_session.execute()
