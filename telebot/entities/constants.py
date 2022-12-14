import os.path

ALLOWED_PORTS = [
    ["2082", "2084", "2083"],
    ["2086", "2087", "2089"]
]
CONFIG_PATH = os.path.join(os.path.abspath('.'), 'config', 'config.json')
DATABASE_PATH = os.path.join(os.path.abspath('.'), 'db', 'database.db')
URL_LOGIN_STRING = '/login/?login_only=1'
URL_DOMAIN_STRING = '/execute/DomainInfo/domains_data'
WHM_DOMAIN_STRING = '/json-api/get_domain_info?api.version=1'
DELIVERABILITY_STRING = '/execute/Batch/strict'
VALIDATE_DOMAIN_DATA = {
    'return_https_redirect_status': 1
}
TIMEOUT = int(os.getenv('TIMEOUT'))
TIMEOUT_VALID = int(os.getenv('TIMEOUT_VALID'))
SEPARATOR = "|"
CHECK_PORTS_ERROR = False
VALIDATOR = 'API'
CHECK_PORTS_WRONG_CREDENTIALS = False
RESTRICTED_CPANEL_DOMAINS = ('sub_domains',)
RESTRICTED_WHM_DOMAINS = ('sub',)
FILE_API_URL = 'https://api.telegram.org/file/bot'
proxies = {
    'http://user98426:3fbyk8@191.101.73.206:3269',
}
CHUNK_SIZE = int(os.getenv('CHUNK_SIZE'))
