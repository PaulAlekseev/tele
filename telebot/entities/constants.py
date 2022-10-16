import os.path


CONFIG_PATH = os.path.join(os.path.abspath('.'), 'config', 'config.json')
DATABASE_PATH = os.path.join(os.path.abspath('.'), 'db', 'database.db')
URL_LOGIN_STRING = '/login/?login_only=1'
URL_DOMAIN_STRING = '/execute/DomainInfo/domains_data'
WHM_DOMAIN_STRING = '/json-api/get_domain_info?api.version=1'
DELIVERABILITY_STRING = '/execute/Batch/strict'
VALIDATE_DOMAIN_DATA = {
    'return_https_redirect_status': 1
}
RESTRICTED_CPANEL_DOMAINS = ('sub_domains', )
RESTRICTED_WHM_DOMAINS = ('sub', )