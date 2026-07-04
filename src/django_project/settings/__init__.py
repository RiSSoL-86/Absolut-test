from pathlib import Path

import environ  # type: ignore[import-untyped]
from split_settings.tools import include as settings_include
from split_settings.tools import optional

BASE_DIR = Path(__file__).resolve().parent.parent.parent
env = environ.Env()
ENV_FILE = BASE_DIR / ".env"
if not ENV_FILE.exists():
    ENV_FILE = BASE_DIR / ".env.example"
environ.Env.read_env(ENV_FILE)

ENVIRONMENT = env("ENVIRONMENT")

# Values exported by split settings modules and imported by later fragments.
PROJECT_NAME: str
TIME_ZONE: str

# each file below reads what it needs from `env`
settings_include(
    "common.py",
    "installed_apps.py",
    "auth.py",
    "rest_framework.py",
    "simple_jwt.py",
    "cache.py",
    "database.py",
    "i18n.py",
    "tz.py",
    "storage.py",
    "celery.py",
    "email.py",
    "logging.py",
    "tests.py",
    "sentry.py",
    optional("local_settings.py"),
)
