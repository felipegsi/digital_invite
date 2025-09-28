from .base import *  # noqa: F401,F403
import os

DEBUG = True

# For development allow a fallback secret key so setup is easy locally
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-development-key')

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Keep default sqlite3 in base for dev (no extra changes required)
# Optionally override any dev-specific settings here