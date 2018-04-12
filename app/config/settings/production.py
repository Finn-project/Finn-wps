from .base import *

secrets = json.loads(open(SECRETS_PRODUCTION, 'rt').read())
set_config(secrets, module_name=__name__, root=True)

DEBUG = True
ALLOWED_HOSTS = [
    '.elasticbeanstalk.com',
    '.himanmen.com'
]
WSGI_APPLICATION = 'config.wsgi.production.application'
INSTALLED_APPS += [
    'storages',
]

DEFAULT_FILE_STORAGE = 'config.storage.DefaultFilesStorage'
# STATICFILES_STORAGE = 'config.storage.StaticFilesStorage'

# Elastic Beanstalk의 ELB Health check 4xx에러 해결 코드(2)
private_ip = get_linux_ec2_private_ip()
if private_ip:
    ALLOWED_HOSTS.append(private_ip)
