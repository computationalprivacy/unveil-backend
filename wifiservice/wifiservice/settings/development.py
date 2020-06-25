"""Development settings file."""
from .base import *


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'l@yif+i_t1de$xe2y&vizech@b@)xfea3o@-k$l8()gpew68+9'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

CORS_ORIGIN_ALLOW_ALL = DEBUG


MONGO_DB = dict(
    host='127.0.0.1',
    port=27017,
    db_name='wifi',
    password=None,
    username=None
)


class DEMO_SECURITY:
    allowed_ips = '127.0.0.1/32'
    security_check_required = not DEBUG
    pin = '3167'


RQ_QUEUES = {
    'data': {
        'HOST': 'localhost',
        'PORT': 6379,
        'DB': 0,
        'PASSWORD': '12345678',
        'DEFAULT_TIMEOUT': 36000,
    },
    'instructions': {
        'HOST': 'localhost',
        'PORT': 6379,
        'DB': 0,
        'PASSWORD': '12345678',
        'DEFAULT_TIMEOUT': 36000,
    }
}
