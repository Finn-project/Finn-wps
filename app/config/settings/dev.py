from .base import *

secrets = json.loads(open(SECRETS_DEV, 'rt').read())
set_config(secrets, module_name=__name__, root=True)

DEBUG = True
ALLOWED_HOSTS = []
WSGI_APPLICATION = 'config.wsgi.dev.application'
INSTALLED_APPS += [
    'django_extensions',
    'storages',
]
