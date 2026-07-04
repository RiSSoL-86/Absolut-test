from typing import final, override

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import F
from django.db.models.functions import Lower
from django.utils.translation import gettext_lazy as _

from apps.common.models import TimeStampedAbstractModel, UUIAbstractModel
from apps.users.choices import Role


@final
class Questionnaire(UUIAbstractModel, TimeStampedAbstractModel):
    """A survey owned by an author and taken by readers."""

    title = models.CharField(_("title"), max_length=255)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="questionnaires",
        limit_choices_to={"role": Role.AUTHOR},
        db_index=False,
    )
    is_published = models.BooleanField(_("published"), default=False)
    question_order = ArrayField(
        models.UUIDField(),
        default=list,
        blank=True,
        help_text=_("ordered ids of this survey's questions"),
    )

    @override
    def __str__(self) -> str:
        return f"{self.title} ({self.author})"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower("title"),
                F("author"),
                name="unique_author_lowered_title",
            )
        ]
        indexes = [
            models.Index(fields=["author", "is_published"]),
            models.Index(
                fields=["is_published", "-created_timestamp"],
                name="quest_published_created_idx",
            ),
        ]
