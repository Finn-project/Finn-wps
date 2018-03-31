from .base import *

secrets = json.loads(open(SECRETS_PRODUCTION, 'rt').read())
set_config(secrets, module_name=__name__, root=True)

DEBUG = False
ALLOWED_HOSTS = []
WSGI_APPLICATION = 'config.wsgi.production.application'
INSTALLED_APPS += [
    'storages',
]
