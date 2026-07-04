INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    # 3rd party apps
    "rest_framework",
    "drf_spectacular",
    "drf_spectacular_sidecar",
    # project apps
    "apps.questionnaires",
    "apps.questions",
    "apps.results",
    "apps.users",
]
