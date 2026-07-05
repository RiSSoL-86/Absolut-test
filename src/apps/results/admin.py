from typing import Any, cast, final, override

from django import forms
from django.contrib import admin
from django.forms.models import BaseInlineFormSet

from apps.questions.models import AnswerOption
from apps.results.models import SurveyAnswer, SurveyResult


@final
class SurveyAnswerAdminForm(forms.ModelForm):  # type: ignore[type-arg]
    """Limit answer choices to the selected result/question where possible."""

    class Meta:
        model = SurveyAnswer
        fields = "__all__"

    @override
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        result_id = (
            self.data.get(self.add_prefix("result"))
            or self.initial.get("result")
            or self.instance.result_id
        )
        question_id = (
            self.data.get(self.add_prefix("question"))
            or self.initial.get("question")
            or self.instance.question_id
        )

        if result_id:
            question_field = cast("Any", self.fields["question"])
            question_field.queryset = question_field.queryset.filter(
                questionnaire__results__id=result_id
            )

        option_field = cast("Any", self.fields["option"])
        if question_id:
            option_field.queryset = option_field.queryset.filter(
                question_id=question_id
            )
        else:
            option_field.queryset = AnswerOption.objects.none()


@final
class SurveyAnswerInlineFormSet(BaseInlineFormSet):  # type: ignore[type-arg]
    """Validate answers that are edited together inside a result."""

    @override
    def clean(self) -> None:
        super().clean()
        single_answered = set()

        for form in self.forms:
            if not hasattr(form, "cleaned_data"):
                continue
            if form.cleaned_data.get("DELETE"):
                continue

            question = form.cleaned_data.get("question")
            if question is None or question.allow_multiple:
                continue

            if question.pk in single_answered:
                raise forms.ValidationError(
                    "This question does not support multiple answers."
                )
            single_answered.add(question.pk)


@final
class SurveyAnswerInline(admin.TabularInline):  # type: ignore[type-arg]
    """Answers listed inline within their result."""

    model = SurveyAnswer
    form = SurveyAnswerAdminForm
    formset = SurveyAnswerInlineFormSet
    fields = ("question", "option")
    autocomplete_fields = ("question",)
    extra = 0


@final
@admin.register(SurveyResult)
class SurveyResultAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    """A user's result, with the answers they gave inline."""

    list_display = (
        "id",
        "questionnaire",
        "respondent",
        "started_timestamp",
        "completed_timestamp",
        "duration",
    )
    list_filter = ("started_timestamp",)
    search_fields = ("respondent__email", "questionnaire__title")
    autocomplete_fields = ("questionnaire", "respondent")
    list_select_related = (
        "questionnaire",
        "questionnaire__author",
        "respondent",
    )
    inlines = (SurveyAnswerInline,)

    @admin.display(description="duration")
    def duration(self, obj: SurveyResult) -> str:
        """Completion time, or a dash while still in progress."""
        if obj.completed_timestamp is None:
            return "—"
        return str(obj.completed_timestamp - obj.started_timestamp)


@final
@admin.register(SurveyAnswer)
class SurveyAnswerAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    """Standalone answer list (also editable inline on a result)."""

    form = SurveyAnswerAdminForm
    list_display = (
        "id",
        "result",
        "question",
        "option",
        "created_timestamp",
    )
    search_fields = ("result__respondent__email",)
    autocomplete_fields = ("result", "question")
