from typing import override

from django.apps import AppConfig


class QuestionsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.questions"

    @override
    def ready(self) -> None:
        from apps.questions import signals  # noqa: F401
