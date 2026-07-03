from django_project.settings import TIME_ZONE, env

CELERY_BROKER_URL = env("CELERY_BROKER_URL")
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TIME_LIMIT = env.int("CELERY_TASK_TIME_LIMIT")
CELERY_TASK_ACKS_LATE = False
CELERY_RESULT_BACKEND = None
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_TASK_DEFAULT_EXCHANGE_TYPE = "direct"
CELERY_BROKER_TRANSPORT_OPTIONS = {
    "visibility_timeout": env.int("CELERY_VISIBILITY_TIMEOUT"),
    "polling_interval": env.int("CELERY_POLLING_INTERVAL"),
}

CELERY_TASK_ROUTES: tuple[list[tuple[str, dict[str, str]]], ...] = ([],)

CELERY_BEAT_SCHEDULE: dict[str, object] = {}

# Task autodiscovery is handled in django_project/celery.py
# No need to manually list imports - discover_celery_tasks() handles this
# automatically
CELERY_IMPORTS = [
    "services.celery_tasks",
]
