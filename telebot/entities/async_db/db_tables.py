from sqlalchemy import String, Integer, Column, Date, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base
from datetime import date

Base = declarative_base()


class Credential(Base):
    __tablename__ = 'credential'
    id = Column(Integer, primary_key=True)
    url = Column(String(200), nullable=False)
    login = Column(String(200), nullable=False)
    password = Column(String(200), nullable=False)
    created = Column(Date, default=date.today)
    updated = Column(Date, default=date.today, onupdate=date.today)
    scan_id = Column(Integer, ForeignKey('scan.id'))


class CaptchaCredential(Base):
    __tablename__ = 'captcha_credential'
    id = Column(Integer, primary_key=True)
    url = Column(String(200), nullable=False)
    login = Column(String(200), nullable=False)
    password = Column(String(200), nullable=False)
    created = Column(Date, default=date.today)
    scan_id = Column(Integer, ForeignKey('scan.id'))


class Domain(Base):
    __tablename__ = 'domain'
    id = Column(Integer, primary_key=True)
    domain = Column(String(200), nullable=False)
    type = Column(String(200), nullable=False)
    status = Column(String(50), nullable=False)
    email = Column(String(10))
    email_dns = Column(String(10))
    credential_id = Column(Integer, ForeignKey('credential.id'))


class Activation(Base):
    __tablename__ = 'activation'
    id = Column(Integer, primary_key=True)
    created = Column(Date, default=date.today)
    expires = Column(Date, nullable=False)
    user_tele_id = Column(Integer, nullable=False)
