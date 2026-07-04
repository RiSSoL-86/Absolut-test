from typing import Any, final, override

from rest_framework import serializers

from apps.questionnaires.models import Questionnaire
from apps.questionnaires.services import QuestionnaireService
from apps.users.models import User
from services.api.questions.serializers import NestedQuestionSerializer


@final
class QuestionnaireAuthorSerializer(serializers.ModelSerializer[User]):
    """Compact author info shown alongside a questionnaire."""

    class Meta:
        model = User
        fields = ("id", "first_name", "last_name")


class QuestionnaireListSerializer(serializers.ModelSerializer[Questionnaire]):
    """A questionnaire as a single feed item."""

    author = QuestionnaireAuthorSerializer(read_only=True)
    question_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Questionnaire
        fields: tuple[str, ...] = (
            "id",
            "title",
            "author",
            "is_published",
            "question_count",
            "created_timestamp",
            "updated_timestamp",
        )


@final
class QuestionnaireDetailSerializer(QuestionnaireListSerializer):
    """A questionnaire with its questions in the author-defined order."""

    questions = serializers.SerializerMethodField()

    class Meta(QuestionnaireListSerializer.Meta):
        fields = (*QuestionnaireListSerializer.Meta.fields, "questions")

    @staticmethod
    def get_questions(obj: Questionnaire) -> Any:
        questions = {question.id: question for question in obj.questions.all()}
        ordered = [
            questions[qid] for qid in obj.question_order if qid in questions
        ]
        return NestedQuestionSerializer(ordered, many=True).data


@final
class QuestionnaireCreateSerializer(
    serializers.ModelSerializer[Questionnaire]
):
    """Create a questionnaire; it starts empty and unpublished."""

    class Meta:
        model = Questionnaire
        fields = ("id", "title")
        read_only_fields = ("id",)

    @override
    def create(self, validated_data: dict[str, Any]) -> Questionnaire:
        return QuestionnaireService.create(
            author_id=validated_data["author_id"],
            title=validated_data["title"],
        )


@final
class QuestionnaireWriteSerializer(serializers.ModelSerializer[Questionnaire]):
    """Update a questionnaire's title and reorder its questions."""

    question_order = serializers.ListField(
        child=serializers.UUIDField(), required=False
    )

    class Meta:
        model = Questionnaire
        fields = ("id", "title", "question_order")
        read_only_fields = ("id",)

    def validate_question_order(self, value: list[Any]) -> list[Any]:
        assert self.instance is not None
        if len(value) != len(set(value)):
            raise serializers.ValidationError(
                "Order must not repeat a question."
            )
        owned = set(self.instance.questions.values_list("id", flat=True))
        if set(value) != owned:
            raise serializers.ValidationError(
                "Order must list every question of this survey exactly once."
            )
        return value

    @override
    def update(
        self, instance: Questionnaire, validated_data: dict[str, Any]
    ) -> Questionnaire:
        return QuestionnaireService.update(
            questionnaire=instance, fields=validated_data
        )
