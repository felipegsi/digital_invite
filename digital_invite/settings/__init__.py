# python
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

_env = os.getenv('DJANGO_ENV', 'dev').lower()

# Do not print on import in production; selection below will import the correct settings module
if _env in ('prod', 'production'):
    from .prod import *  # noqa: F401,F403
elif _env in ('dev', 'development'):
    from .dev import *  # noqa: F401,F403
else:
    raise ImportError(f"Environment '{_env}' does not exist. Please check your DJANGO_ENV variable.")
