from datetime import datetime

from OpenSSL import SSL
from cryptography import x509
from cryptography.x509 import Certificate
from cryptography.x509.oid import NameOID
import idna
from socket import socket

from entities.constants import RESTRICTED_CPANEL_DOMAINS, RESTRICTED_WHM_DOMAINS
from entities.user import User
from entities.validator import APIValidator


def change_credentials_password(credentials: dict) -> dict:
    new_credentials = credentials.copy()
    new_credentials.update({
        'pass': credentials['pass'] + '1'
    })
    return new_credentials


def get_common_name(cert):
    try:
        names = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)
        return names[0].value
    except x509.ExtensionNotFound:
        return None


def get_issuer(cert):
    try:
        names = cert.issuer.get_attributes_for_oid(NameOID.COMMON_NAME)
        return names[0].value
    except x509.ExtensionNotFound:
        return None


def get_cert(domain):
    try:
        hostname_idna = idna.encode(domain)
        sock = socket()

        sock.connect((domain, 443))
        ctx = SSL.Context(SSL.SSLv23_METHOD)
        ctx.check_hostname = False
        ctx.verify_mode = SSL.VERIFY_NONE

        sock_ssl = SSL.Connection(ctx, sock)
        sock_ssl.set_connect_state()
        sock_ssl.set_tlsext_host_name(hostname_idna)
        sock_ssl.do_handshake()
        cert = sock_ssl.get_peer_certificate()
        crypto_cert = cert.to_cryptography()
        sock_ssl.close()
        sock.close()
    except Exception:
        crypto_cert = None
    return crypto_cert


def get_ssl_status(cert: Certificate):
    expire_date = cert.not_valid_after
    if get_common_name(cert) == get_issuer(cert):
        return 'Self-signed'
    if expire_date < datetime.now():
        return 'Expired'
    return 'Valid'


def gather_cpanel_domains(data: dict):
    try:
        result = []
        for key, item in data.items():
            if key not in RESTRICTED_CPANEL_DOMAINS:
                if not isinstance(item, list):
                    result.append((item.get('domain'), key, ))
                else:
                    for sub_item in item:
                        if isinstance(sub_item, str):
                            result.append((sub_item, key, ))
                        else:
                            result.append((sub_item.get('domain'), key, ))
        return result
    except Exception:
        return None


def gather_whm_domains(data: dict):
    try:
        result = []
        for item in data['domains']:
            domain_type = item.get('domain_type')
            if domain_type not in RESTRICTED_WHM_DOMAINS:
                if isinstance(item, str):
                    result.append((item, domain_type, ))
                else:
                    result.append((item.get('domain'), domain_type, ))
        return result
    except Exception:
        return None


def validate(data: dict) -> dict:
    user = User(data)
    data = APIValidator().get_deliverability(user)
    if data.get('result') == 0:


