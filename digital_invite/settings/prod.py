# python
# file: digital_invite/settings/prod.py
from .base import *  # noqa: F401,F403
import os
from django.core.exceptions import ImproperlyConfigured

DEBUG = False

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise ImproperlyConfigured('DJANGO_SECRET_KEY environment variable is required for production')

# ALLOWED_HOSTS deve vir de uma variável de ambiente (comma-separated)
allowed = os.getenv('DJANGO_ALLOWED_HOSTS', '')
ALLOWED_HOSTS = [h.strip() for h in allowed.split(',') if h.strip()]

# Usar a configuração `DATABASES` definida em `digital_invite/settings/base.py`
# (não redefina aqui para evitar duplicação).

# Security hardening
SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', '1') == '1'
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', '31536000'))
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
