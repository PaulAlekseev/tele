import datetime
import sqlalchemy
from sqlalchemy import func, desc

from sqlalchemy.orm import Session

from entities.async_db.db_specifications import ScanSpecification
from entities.db.db_engine import engine
from entities.db.db_tables import Credential, CaptchaCredential, Scan, Domain, User


class CredentialsRepository:
    model = Credential

    def _save_object(self, session, obj):
        session.add(obj)
        session.commit()

    def add(self, url, login, password, scan_id):
        with Session(bind=engine) as session:
            try:
                credentials = session.query(self.model).filter(
                    self.model.url == url,
                    self.model.login == login,
                    self.model.password == password,
                ).one()
            except sqlalchemy.orm.exc.NoResultFound:
                credentials = self.model(
                    url=url,
                    login=login,
                    password=password,
                    scan_id=scan_id,
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

    def get_by_session(self, session_id):
        with Session(bind=engine) as session:
            result = session.query(self.model).filter(
                self.model.scan_id == session_id
            ).all()
        return result


class CaptchaCredentialsRepository:
    model = CaptchaCredential

    def _save_object(self, session, obj):
        session.add(obj)
        session.commit()

    def add_or_update(self, url, login, password, scan_id):
        with Session(bind=engine) as session:
            try:
                credentials = session.query(self.model).filter(
                    self.model.url == url,
                    self.model.login == login,
                    self.model.password == password,
                ).one()
            except sqlalchemy.orm.exc.NoResultFound:
                credentials = self.model(
                    url=url,
                    login=login,
                    password=password,
                    scan_id=scan_id
                )
            self._save_object(session, credentials)
        return credentials

    def get_by_id(self, session_id: int):
        with Session(bind=engine) as session:
            result = session.query(self.model).filter(
                self.model.scan_id == session_id
            ).all()
        return result

    def remove(self, url, login, password):
        with Session(bind=engine) as session:
            session.query(self.model).filter(
                self.model.url == url,
                self.model.login == login,
                self.model.password == password,
            ).delete(synchronize_session=False)
            session.commit()


class ScanRepository:
    model = Scan

    def get(self, scan_specification: ScanSpecification):
        with Session(bind=engine) as session:
            scan = session.query(self.model).filter(
                scan_specification.is_satisfied()
            )
        return scan

    def get_latest(self) -> Scan:
        with Session(bind=engine) as session:
            scan = session.query(self.model).order_by(
                desc('created')
            ).first()
        return scan


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
