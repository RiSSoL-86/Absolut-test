from typing import Any, final, override

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


@final
class SurveyResult(models.Model):
    """A single user's result for a questionnaire."""

    questionnaire = models.ForeignKey(
        "questionnaires.Questionnaire",
        on_delete=models.CASCADE,
        related_name="results",
        db_index=False,
    )
    respondent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="results",
    )
    started_timestamp = models.DateTimeField(
        _("started at"), auto_now_add=True
    )
    completed_timestamp = models.DateTimeField(
        _("completed at"), null=True, blank=True
    )

    @override
    def __str__(self) -> str:
        return f"{self.questionnaire} - {self.respondent}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["questionnaire", "respondent"],
                name="unique_survey_result_per_user",
            )
        ]


@final
class SurveyAnswer(models.Model):
    """A selected option inside a survey result."""

    result = models.ForeignKey(
        SurveyResult,
        on_delete=models.CASCADE,
        related_name="answers",
        db_index=False,
    )
    question = models.ForeignKey(
        "questions.Question",
        on_delete=models.PROTECT,
        related_name="answers",
        db_index=False,
    )
    option = models.ForeignKey(
        "questions.AnswerOption",
        on_delete=models.PROTECT,
        related_name="answers",
    )
    created_timestamp = models.DateTimeField(
        _("created at"), auto_now_add=True
    )

    @override
    def clean(self) -> None:
        errors = {}

        if self.question_id and self.option_id:
            if self.option.question_id != self.question_id:
                errors["option"] = _(
                    "Selected option does not belong to the selected question."
                )

        if self.result_id and self.question_id:
            if self.question.questionnaire_id != self.result.questionnaire_id:
                errors["question"] = _(
                    "Selected question does not belong to "
                    "the result questionnaire."
                )

            has_answer = SurveyAnswer.objects.filter(
                result_id=self.result_id,
                question_id=self.question_id,
            )
            if self.pk is not None:
                has_answer = has_answer.exclude(pk=self.pk)

            if has_answer.exists() and not self.question.allow_multiple:
                errors["question"] = _(
                    "This question does not support multiple answers."
                )

        if errors:
            raise ValidationError(errors)

    @override
    def save(self, *args: Any, **kwargs: Any) -> None:
        """Enforce ``clean()`` on every write path, not just admin forms."""
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["result", "question", "option"],
                name="unique_survey_answer_per_option",
            )
        ]
        indexes = [models.Index(fields=["question", "option"])]
