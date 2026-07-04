from typing import Any, final, override

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.questions.models import AnswerOption, Question
from apps.questions.services import AnswerOptionService, QuestionService


@final
class NestedOptionSerializer(serializers.ModelSerializer[AnswerOption]):
    """An answer option as it appears inside its question."""

    class Meta:
        model = AnswerOption
        fields = ("id", "text")


class NestedQuestionSerializer(serializers.ModelSerializer[Question]):
    """A question with its options, as it appears inside a questionnaire."""

    options = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields: tuple[str, ...] = ("id", "text", "allow_multiple", "options")

    @staticmethod
    @extend_schema_field(NestedOptionSerializer(many=True))
    def get_options(obj: Question) -> Any:
        options = {option.id: option for option in obj.options.all()}
        ordered = [options[oid] for oid in obj.option_order if oid in options]
        return NestedOptionSerializer(ordered, many=True).data


@final
class QuestionDetailSerializer(NestedQuestionSerializer):
    """A single question with its parent questionnaire and options."""

    class Meta(NestedQuestionSerializer.Meta):
        fields = ("id", "questionnaire", "text", "allow_multiple", "options")


@final
class QuestionCreateSerializer(serializers.ModelSerializer[Question]):
    """Create a question inside a draft questionnaire."""

    class Meta:
        model = Question
        fields = ("id", "questionnaire", "text", "allow_multiple")
        read_only_fields = ("id",)

    @override
    def create(self, validated_data: dict[str, Any]) -> Question:
        return QuestionService.create(
            questionnaire=validated_data["questionnaire"],
            text=validated_data["text"],
            allow_multiple=validated_data.get("allow_multiple", False),
        )


@final
class QuestionWriteSerializer(serializers.ModelSerializer[Question]):
    """Edit a question's text and reorder its options."""

    option_order = serializers.ListField(
        child=serializers.UUIDField(), required=False
    )

    class Meta:
        model = Question
        fields = ("id", "text", "allow_multiple", "option_order")
        read_only_fields = ("id",)

    def validate_option_order(self, value: list[Any]) -> list[Any]:
        assert self.instance is not None
        if len(value) != len(set(value)):
            raise serializers.ValidationError(
                "Order must not repeat an option."
            )
        owned = set(self.instance.options.values_list("id", flat=True))
        if set(value) != owned:
            raise serializers.ValidationError(
                "Order must list every option of this question exactly once."
            )
        return value

    @override
    def update(
        self, instance: Question, validated_data: dict[str, Any]
    ) -> Question:
        return QuestionService.update(question=instance, fields=validated_data)


@final
class OptionDetailSerializer(serializers.ModelSerializer[AnswerOption]):
    """A single answer option with its parent question."""

    class Meta:
        model = AnswerOption
        fields = ("id", "question", "text")


@final
class OptionCreateSerializer(serializers.ModelSerializer[AnswerOption]):
    """Create an option inside a question."""

    class Meta:
        model = AnswerOption
        fields = ("id", "question", "text")
        read_only_fields = ("id",)

    @override
    def create(self, validated_data: dict[str, Any]) -> AnswerOption:
        return AnswerOptionService.create(
            question=validated_data["question"],
            text=validated_data["text"],
        )


@final
class OptionWriteSerializer(serializers.ModelSerializer[AnswerOption]):
    """Edit an option's text."""

    class Meta:
        model = AnswerOption
        fields = ("id", "text")
        read_only_fields = ("id",)

    @override
    def update(
        self, instance: AnswerOption, validated_data: dict[str, Any]
    ) -> AnswerOption:
        return AnswerOptionService.update(
            option=instance, fields=validated_data
        )
