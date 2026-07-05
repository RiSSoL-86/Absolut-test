from typing import TYPE_CHECKING, Any, final

from django.db.models import Count, Q

from apps.questionnaires.models import Questionnaire

if TYPE_CHECKING:
    from django.db.models import QuerySet


@final
class QuestionnaireService:
    """Read- and write-side operations for questionnaires."""

    @staticmethod
    def get(user_id: int, is_staff: bool) -> QuerySet[Questionnaire]:
        """Return visible questionnaires for detail retrieval."""
        queryset = (
            Questionnaire.objects.select_related("author")
            .annotate(question_count=Count("questions"))
            .prefetch_related("questions__options")
        )
        if is_staff:
            return queryset
        return queryset.filter(Q(is_published=True) | Q(author_id=user_id))

    @staticmethod
    def get_all(user_id: int, is_staff: bool) -> QuerySet[Questionnaire]:
        """Return all visible questionnaires, newest first."""
        queryset = (
            Questionnaire.objects.select_related("author")
            .annotate(question_count=Count("questions"))
            .order_by("-created_timestamp")
        )
        if is_staff:
            return queryset
        return queryset.filter(Q(is_published=True) | Q(author_id=user_id))

    @staticmethod
    def create(
        author_id: int, title: str, is_published: bool = False
    ) -> Questionnaire:
        """Create a questionnaire owned by the given author."""
        return Questionnaire.objects.create(
            author_id=author_id, title=title, is_published=is_published
        )

    @staticmethod
    def update(
        questionnaire: Questionnaire, fields: dict[str, Any]
    ) -> Questionnaire:
        """Apply the given field changes and save."""
        for field, value in fields.items():
            setattr(questionnaire, field, value)
        questionnaire.save()
        return questionnaire

    @staticmethod
    def is_publishable(questionnaire: Questionnaire) -> bool:
        """True if there is at least one question and each one has options."""
        questions = questionnaire.questions.annotate(
            option_count=Count("options")
        )
        return (
            questions.exists()
            and not questions.filter(option_count=0).exists()
        )

    @staticmethod
    def publish(questionnaire: Questionnaire) -> Questionnaire:
        """Freeze the questionnaire so respondents can take it."""
        questionnaire.is_published = True
        questionnaire.save(update_fields=["is_published", "updated_timestamp"])
        return questionnaire
