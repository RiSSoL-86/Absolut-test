from typing import Any, final
from urllib.parse import urlencode

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from apps.common.admin import ArrayOrderedInline, ArrayOrderedParentAdmin
from apps.questionnaires.models import Questionnaire
from apps.questions.models import Question


@final
class QuestionInline(ArrayOrderedInline):
    """Survey questions in order; edit via change link."""

    model = Question
    fields = ("reorder", "allow_multiple")
    order_field = "question_order"
    parent_fk = "questionnaire"


@final
@admin.register(Questionnaire)
class QuestionnaireAdmin(ArrayOrderedParentAdmin):
    """A survey with its questions inline, reorderable in place."""

    child_model = Question
    child_fk = "questionnaire"
    child_related_name = "questions"
    order_field = "question_order"

    list_display = (
        "title",
        "author",
        "is_published",
        "question_count",
        "created_timestamp",
    )
    readonly_fields = (
        "created_timestamp",
        "updated_timestamp",
        "add_question_link",
    )
    list_filter = ("is_published",)
    search_fields = ("title",)
    autocomplete_fields = ("author",)
    exclude = ("question_order",)
    inlines = (QuestionInline,)

    @admin.display(description="Add question")
    def add_question_link(self, obj: Questionnaire | None = None) -> Any:
        if obj is None:
            return ""

        url = reverse("admin:questions_question_add")
        query = urlencode({"questionnaire": obj.pk})
        return format_html(
            '<a class="button" href="{}?{}">Add another Question</a>',
            url,
            query,
        )

    @admin.display(description="questions", ordering="child_count")
    def question_count(self, obj: Any) -> int:
        """Number of questions in the survey (annotated in get_queryset)."""
        return int(obj.child_count)
