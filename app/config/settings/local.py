from .base import *

secrets = json.loads(open(SECRETS_LOCAL, 'rt').read())
set_config(secrets, __name__, root=True)

DEBUG = True
ALLOWED_HOSTS = []
WSGI_APPLICATION = 'config.wsgi.local.application'
INSTALLED_APPS += [
    'django_extensions'
]
