import datetime
import sqlalchemy
from sqlalchemy.orm import Session

from entities.db.db_engine import engine
from entities.db.db_tables import Credential, Domain, User, Activation


class CredentialsRepository:
    model = Credential

    def _save_object(self, session, obj):
        session.add(obj)
        session.commit()

    def add(self, url, login, password, region):
        with Session(bind=engine) as session:
            try:
                credentials = session.query(self.model).filter(
                    self.model.url == url,
                    self.model.login == login,
                    self.model.password == password,
                    self.model.region == region
                ).one()
            except sqlalchemy.orm.exc.NoResultFound:
                credentials = self.model(
                    url=url,
                    login=login,
                    password=password,
                    region=region
                )
                self._save_object(session, credentials)
                session.refresh(credentials)
                session.expunge(credentials)
            return credentials

    def get_by_date(self, requested_date: datetime.date):
        with Session(bind=engine) as session:
            result = session.query(self.model).filter(
                self.model.created == requested_date
            ).all()
        return result

    def get_by_date_range(self, date1: datetime.date, date2: datetime.date):
        with Session(bind=engine) as session:
            result = session.query(self.model).filter(
                self.model.created >= date1,
                self.model.created <= date2,
            ).all()
        return result


class DomainRepository:
    model = Domain

    def add_or_update(self, data: dict, credentials_id: int):
        with Session(bind=engine) as session:
            credentials = session.query(self.model).filter(
                self.model.credential_id == credentials_id
            ).first()
            if not credentials and data.get('domains'):
                for item in data['domains'].values():
                    email = item.get('email')
                    if not isinstance(email, bool):
                        email = 'No Info'
                    else:
                        if email:
                            email = 'Valid'
                        else:
                            email = 'Not Valid'
                    email_dns = item.get('dns_email')
                    if not isinstance(email_dns, bool):
                        email_dns = 'No Info'
                    else:
                        if email_dns:
                            email_dns = 'Valid'
                        else:
                            email_dns = 'Not Valid'
                    result_model = self.model(
                        domain=item['domain'],
                        type=item['type'],
                        status=item['ssl_status'],
                        email=email,
                        email_dns=email_dns,
                        credential_id=credentials_id,
                    )
                    if credentials:
                        result_model.id = credentials
                    session.add(result_model)
                    session.commit()


class CredentialDomainRepository:
    model1 = Domain
    model2 = Credential

    def get_by_session(self, session_id):
        with Session(bind=engine) as session:
            credential_result = session.query(self.model2).filter(
                self.model2.scan_id == session_id
            ).all()
            credential_ids = [item.id for item in credential_result]
            domain_result = session.query(self.model1).filter(
                self.model1.credential_id.in_(credential_ids)
            ).all()
        result = {
            str(item.id): {
                'region': item.region,
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
                        'name': item.domain,
                        'type': item.type,
                        'status': item.status,
                        'email': item.email,
                        'email_dns': item.email_dns,
                    }
                })
        return result

    def get_by_date_range(self, date1, date2):
        with Session(bind=engine) as session:
            credential_result = session.query(self.model2).filter(
                self.model2.created >= date1,
                self.model2.created <= date2,
            ).all()
            credential_ids = [item.id for item in credential_result]
            domain_result = session.query(self.model1).filter(
                self.model1.credential_id.in_(credential_ids)
            ).all()
        result = {
            str(item.id): {
                'region': item.region,
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
                        'name': item.domain,
                        'type': item.type,
                        'status': item.status,
                        'email': item.email,
                        'email_dns': item.email_dns,
                    }
                })
        return result


class UserRepo:
    model = User

    def add_to_count(self, tele_id, amount) -> None:
        with Session(bind=engine) as session:
            user = session.query(self.model).filter(
                self.model.tele_id == str(tele_id)
            ).first()
            user.count += amount
            session.add(user)
            session.commit()


class ActivationRepo:
    model = Activation

    def get(self, id: str) -> Activation:
        with Session(bind=engine) as session:
            activation = session.query(self.model).filter(
                self.model.id == id,
            ).first()
            return activation

    def update(self, activation: Activation):
        with Session(bind=engine) as session:
            session.add(activation)
            session.commit()
