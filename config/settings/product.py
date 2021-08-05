# base.pyから共通設定をインポート
from .base import *

DEBUG = False

ALLOWED_HOSTS = ['donelist.net', 'www.donelist.net']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env('DB_NAME'),
        'HOST': '/opt/bitnami/mariadb/tmp/mysql.sock',
        'PORT': '3306',
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASS')
    }
}

STATIC_ROOT = BASE_DIR / 'static_files'

# HTTPS settings
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

