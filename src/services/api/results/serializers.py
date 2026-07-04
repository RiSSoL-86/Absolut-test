from typing import Any, final, override

from rest_framework import serializers

from apps.results.services import SurveyResultService


@final
class SingleAnswerSerializer(serializers.Serializer[Any]):
    """One question and the option(s) chosen for it."""

    question = serializers.UUIDField()
    options = serializers.ListField(
        child=serializers.UUIDField(), allow_empty=False
    )


@final
class AnswersSerializer(serializers.Serializer[Any]):
    """A batch of answers submitted for a questionnaire."""

    answers = SingleAnswerSerializer(many=True, allow_empty=False)

    @override
    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        questionnaire = self.context["questionnaire"]
        respondent_id = self.context["respondent_id"]
        items = attrs["answers"]

        question_ids = [item["question"] for item in items]
        if len(question_ids) != len(set(question_ids)):
            raise serializers.ValidationError(
                "A question appears more than once."
            )

        questions = {
            question.id: question
            for question in questionnaire.questions.prefetch_related("options")
        }
        already = SurveyResultService.answered_question_ids(
            questionnaire_id=questionnaire.id, respondent_id=respondent_id
        )

        for item in items:
            question = questions.get(item["question"])
            if question is None:
                raise serializers.ValidationError(
                    "Unknown question for this questionnaire."
                )
            if question.id in already:
                raise serializers.ValidationError(
                    "This question has already been answered."
                )
            chosen = item["options"]
            if len(chosen) != len(set(chosen)):
                raise serializers.ValidationError(
                    "An option is chosen more than once."
                )
            owned = {option.id for option in question.options.all()}
            if not set(chosen) <= owned:
                raise serializers.ValidationError(
                    "An option does not belong to its question."
                )
            if not question.allow_multiple and len(chosen) != 1:
                raise serializers.ValidationError(
                    "This question takes exactly one option."
                )
        return attrs


@final
class StatsOptionSerializer(serializers.Serializer[Any]):
    """Answer option popularity inside a stats response."""

    option = serializers.UUIDField()
    text = serializers.CharField()
    count = serializers.IntegerField()


@final
class StatsQuestionSerializer(serializers.Serializer[Any]):
    """Per-question answer distribution inside a stats response."""

    question = serializers.UUIDField()
    options = StatsOptionSerializer(many=True)


@final
class StatsSerializer(serializers.Serializer[Any]):
    """Response counts, answer distribution and average completion time."""

    responses = serializers.IntegerField()
    completed = serializers.IntegerField()
    average_duration_seconds = serializers.FloatField(allow_null=True)
    questions_total = serializers.IntegerField()
    questions = StatsQuestionSerializer(many=True)
