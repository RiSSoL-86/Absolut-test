import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import ignore_logger

from django_project.settings import ENVIRONMENT, env

if SENTRY_DSN := env("SENTRY_DSN"):
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration(), CeleryIntegration()],
        auto_session_tracking=env.bool("SENTRY_AUTO_SESSION_TRACKING"),
        traces_sample_rate=env.float("SENTRY_TRACES_SAMPLE_RATE"),
        environment=ENVIRONMENT,
    )
    ignore_logger("django.security.DisallowedHost")
