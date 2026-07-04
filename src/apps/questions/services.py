from typing import TYPE_CHECKING, Any, final

from django.db.models import Q

from apps.questions.models import AnswerOption, Question

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from apps.questionnaires.models import Questionnaire


@final
class QuestionService:
    """Read- and write-side operations for questions."""

    @staticmethod
    def get(user_id: int, is_staff: bool) -> QuerySet[Question]:
        """Return visible questions for detail retrieval."""
        queryset = Question.objects.select_related(
            "questionnaire"
        ).prefetch_related("options")
        if is_staff:
            return queryset
        return queryset.filter(
            Q(questionnaire__is_published=True)
            | Q(questionnaire__author_id=user_id)
        )

    @staticmethod
    def create(
        questionnaire: Questionnaire,
        text: str,
        allow_multiple: bool = False,
    ) -> Question:
        """Create a question inside the given questionnaire."""
        return Question.objects.create(
            questionnaire=questionnaire,
            text=text,
            allow_multiple=allow_multiple,
        )

    @staticmethod
    def update(question: Question, fields: dict[str, Any]) -> Question:
        """Apply the given field changes and save."""
        for field, value in fields.items():
            setattr(question, field, value)
        question.save()
        return question


@final
class AnswerOptionService:
    """Read- and write-side operations for answer options."""

    @staticmethod
    def get(user_id: int, is_staff: bool) -> QuerySet[AnswerOption]:
        """Return visible options for detail retrieval."""
        queryset = AnswerOption.objects.select_related(
            "question__questionnaire"
        )
        if is_staff:
            return queryset
        return queryset.filter(
            Q(question__questionnaire__is_published=True)
            | Q(question__questionnaire__author_id=user_id)
        )

    @staticmethod
    def create(question: Question, text: str) -> AnswerOption:
        """Create an option inside the given question."""
        return AnswerOption.objects.create(question=question, text=text)

    @staticmethod
    def update(option: AnswerOption, fields: dict[str, Any]) -> AnswerOption:
        """Apply the given field changes and save."""
        for field, value in fields.items():
            setattr(option, field, value)
        option.save()
        return option
