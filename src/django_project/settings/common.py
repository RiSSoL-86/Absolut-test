from django_project.settings import BASE_DIR, ENVIRONMENT, env

DEBUG = env.bool("DEBUG")

# preventing DEBUG mode for non-local environment
if DEBUG and ENVIRONMENT != "local":
    raise ValueError("DEBUG mode should be disabled for non-local environment")

SECRET_KEY = env("SECRET_KEY")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS")

# Middleware configuration
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

ROOT_URLCONF = "django_project.urls"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

FORCE_SCRIPT_NAME = env("SCRIPT_NAME")

if FORCE_SCRIPT_NAME:
    SESSION_COOKIE_PATH = f"{FORCE_SCRIPT_NAME}/"

SILENCED_SYSTEM_CHECKS = ["auth.E003"]

# Project-specific settings
SITE_URL = env("SITE_URL")
PROJECT_NAME = env("PROJECT_NAME")
DOMAIN_NAME = SITE_URL
