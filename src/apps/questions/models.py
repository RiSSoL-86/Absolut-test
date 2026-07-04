from typing import final, override

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models.functions import Lower
from django.utils.translation import gettext_lazy as _

from apps.common.models import TimeStampedAbstractModel, UUIAbstractModel


@final
class Question(UUIAbstractModel, TimeStampedAbstractModel):
    """A question inside a questionnaire; its options' order lives here."""

    questionnaire = models.ForeignKey(
        "questionnaires.Questionnaire",
        on_delete=models.CASCADE,
        related_name="questions",
    )
    text = models.TextField(_("text"))
    allow_multiple = models.BooleanField(_("allow multiple"), default=False)
    option_order = ArrayField(
        models.UUIDField(),
        default=list,
        blank=True,
        help_text=_("ordered ids of this question's options"),
    )

    @override
    def __str__(self) -> str:
        return f"{self.text} ({self.questionnaire})"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower("text"),
                "questionnaire",
                name="unique_questionnaire_lowered_question_text",
            )
        ]


@final
class AnswerOption(UUIAbstractModel, TimeStampedAbstractModel):
    """A selectable option of a question."""

    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="options"
    )
    text = models.CharField(_("text"), max_length=500)

    @override
    def __str__(self) -> str:
        return self.text

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower("text"),
                "question",
                name="unique_question_lowered_option_text",
            )
        ]
