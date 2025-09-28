# python
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

_env = os.getenv('DJANGO_ENV', 'dev').lower()

# Opção simples: print (útil em dev)
print(f"--------> Loading settings: { _env } <--------")

if _env in ('prod', 'production'):
    from .prod import *  # noqa: F401,F403
elif _env in ('dev', 'development'):
    from .dev import *  # noqa: F401,F403
else:
    raise ImportError(f"Environment '{_env}' does not exist. Please check your DJANGO_ENV variable.")
