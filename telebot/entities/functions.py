import io
import os
from datetime import datetime
from typing import List

from OpenSSL import SSL
from cryptography import x509
from cryptography.x509 import Certificate
from cryptography.x509.oid import NameOID
import idna
from socket import socket

from entities.async_db.db_tables import User
from entities.constants import RESTRICTED_CPANEL_DOMAINS, RESTRICTED_WHM_DOMAINS, SEPARATOR
from entities.db.db_repos import CredentialsRepository, DomainRepository


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

        sock.settimeout(float(os.getenv('SSL_SOCKET_TIMEOUT')))
        sock.connect((domain, 443))
        ctx = SSL.Context(SSL.SSLv23_METHOD)
        ctx.set_timeout(int(os.getenv('SSL_TIMEOUT')))
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
                    result.append((item.get('domain'), key,))
                else:
                    for sub_item in item:
                        if isinstance(sub_item, str):
                            result.append((sub_item, key,))
                        else:
                            result.append((sub_item.get('domain'), key,))
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
                    result.append((item, domain_type,))
                else:
                    result.append((item.get('domain'), domain_type,))
        return result
    except Exception:
        return None


def add_credentials_to_db(data: List[dict]) -> List[dict]:
    credentials_repo = CredentialsRepository()
    domain_repo = DomainRepository()
    for credential in data:
        credential_db_entity = credentials_repo.add(
            url=credential.get('url'),
            login=credential['credentials'].get('user'),
            password=credential['credentials'].get('pass'),
            path=credential.get('path'),
            panel_type=credential.get('panel_type'),
        )
        if credential.get('domains'):
            if len(credential.get('domains')) > 0:
                domain_repo.add_or_update(
                    data=credential,
                    credentials_id=credential_db_entity.id,
                )
    return data


def form_credentials_client(data: List[dict]) -> io.BytesIO:
    string = io.BytesIO()
    data = change_info(data)
    for item in data:
        semi_result = f"""{item['path']}{SEPARATOR}{item['url']}{SEPARATOR}{item['credentials']['user']}{SEPARATOR}{item['credentials']['pass']}
    """
        if item.get('domains'):
            for domain in item['domains'].values():
                semi_result += f"""    {domain['domain']}{SEPARATOR}{domain['type']}
    """
        string.write(bytes(semi_result, 'UTF-8'))
        string.write(bytes('\n', 'UTF-8'))
    string.seek(0)
    return string


def form_credentials_admin(data: List[dict]) -> io.BytesIO:
    string = io.BytesIO()
    data = change_info(data)
    string.write(bytes(f'{str(len(data))}\n', 'UTF-8'))
    if data:
        for item in data:
            semi_result = f"""{item['path']}{SEPARATOR}{item['url']}{SEPARATOR}{item['credentials']['user']}{SEPARATOR}{item['credentials']['pass']}
            """
            if item.get('domains'):
                for domain in item['domains'].values():
                    semi_result += f"""    {domain['domain']}{SEPARATOR}{domain['type']}{SEPARATOR}{domain['ssl_status']}{SEPARATOR}{domain['email']}{SEPARATOR}{domain['dns_email']}
        """
            string.write(bytes(semi_result, 'UTF-8'))
            string.write(bytes('\n', 'UTF-8'))
    string.seek(0)
    return string


def change_info(data: List[dict]) -> List[dict]:
    for item in data:
        if item.get('domains'):
            for domain in item['domains'].values():
                if not domain.get('email'):
                    domain['email'] = 'No info'
                    domain['dns_email'] = 'No info'
    return data


def form_user_statistics(data: List[User]) -> io.BytesIO:
    string = io.BytesIO()
    for item in data:
        string.write(bytes(f'{item.tele_id} - {item.count}', 'UTF-8'))
        string.write(bytes('\n', 'UTF-8'))
    string.seek(0)
    return string
