from typing import Any, final
from urllib.parse import urlencode

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from apps.common.admin import ArrayOrderedInline, ArrayOrderedParentAdmin
from apps.questions.models import AnswerOption, Question


@final
class AnswerOptionInline(ArrayOrderedInline):
    """Options of a question in order; reorder on the right."""

    model = AnswerOption
    fields = ("reorder",)
    order_field = "option_order"
    parent_fk = "question"


@final
@admin.register(Question)
class QuestionAdmin(ArrayOrderedParentAdmin):
    """A question with its options inline, reorderable in place."""

    child_model = AnswerOption
    child_fk = "question"
    child_related_name = "options"
    order_field = "option_order"

    list_display = (
        "text",
        "questionnaire",
        "allow_multiple",
        "option_count",
        "created_timestamp",
    )
    list_filter = ("allow_multiple",)
    search_fields = ("text",)
    autocomplete_fields = ("questionnaire",)
    list_select_related = ("questionnaire", "questionnaire__author")
    readonly_fields = (
        "created_timestamp",
        "updated_timestamp",
        "add_option_link",
    )
    exclude = ("option_order",)
    inlines = (AnswerOptionInline,)

    @admin.display(description="Add option")
    def add_option_link(self, obj: Question | None = None) -> Any:
        if obj is None:
            return ""

        url = reverse("admin:questions_answeroption_add")
        query = urlencode({"question": obj.pk})
        return format_html(
            '<a class="button" href="{}?{}">Add another Answer option</a>',
            url,
            query,
        )

    @admin.display(description="Answer options", ordering="child_count")
    def option_count(self, obj: Any) -> int:
        """Number of options on the question (annotated in get_queryset)."""
        return int(obj.child_count)


@final
@admin.register(AnswerOption)
class AnswerOptionAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    """Standalone option list."""

    list_display = ("text", "question", "created_timestamp")
    search_fields = ("text",)
    autocomplete_fields = ("question",)
    readonly_fields = ("created_timestamp", "updated_timestamp")
