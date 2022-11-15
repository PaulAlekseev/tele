from sqlalchemy import String, Integer, Column, Date, ForeignKey, Boolean, BigInteger
from sqlalchemy.orm import declarative_base
from datetime import date

Base = declarative_base()


class Credential(Base):
    __tablename__ = 'credential'
    id = Column(Integer, primary_key=True)
    url = Column(String(200), nullable=False)
    login = Column(String(200), nullable=False)
    password = Column(String(200), nullable=False)
    region = Column(String(20), nullable=False)
    created = Column(Date, default=date.today)
    updated = Column(Date, default=date.today, onupdate=date.today)


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
    user_tele_id = Column(String(50), nullable=False)
    # Amount check is editable and amount daily is not
    amount_daily = Column(BigInteger, nullable=False)
    amount_month = Column(BigInteger, nullable=False)
    amount_once = Column(BigInteger, nullable=False)
    date_check = Column(Date, default=date.today)
    amount_check = Column(BigInteger, nullable=False)


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    tele_id = Column(String(50), nullable=False)
    count = Column(Integer, default=0)


class ActivationType(Base):
    __tablename__ = 'activation_type'
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    amount_once = Column(String(50), nullable=False)
    amount_daily = Column(String(50), nullable=False)
    amount_month = Column(String(50), nullable=False)
    price = Column(String(30), nullable=False)
    active = Column(Boolean, nullable=False)
