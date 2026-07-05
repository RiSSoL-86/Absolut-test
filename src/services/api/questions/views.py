from typing import TYPE_CHECKING, final, override

from rest_framework.generics import (
    CreateAPIView,
    RetrieveUpdateDestroyAPIView,
)

from apps.questions.models import AnswerOption, Question
from apps.questions.services import AnswerOptionService, QuestionService
from services.api.questions.permissions import (
    OptionPermission,
    QuestionPermission,
)
from services.api.questions.serializers import (
    OptionCreateSerializer,
    OptionDetailSerializer,
    OptionWriteSerializer,
    QuestionCreateSerializer,
    QuestionDetailSerializer,
    QuestionWriteSerializer,
)
from services.api.questions.utils import assert_draft_owned
from services.jwt_extensions.services import TokenService

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from rest_framework.serializers import BaseSerializer


@final
class QuestionCreateView(CreateAPIView[Question]):
    """Attach a new question to a draft questionnaire the requester owns."""

    serializer_class = QuestionCreateSerializer
    permission_classes = (QuestionPermission,)

    @override
    def perform_create(self, serializer: BaseSerializer[Question]) -> None:
        questionnaire = serializer.validated_data["questionnaire"]
        token = self.request.auth
        assert_draft_owned(questionnaire=questionnaire, token=token)  # type: ignore[arg-type]
        serializer.save()


@final
class QuestionDetailView(RetrieveUpdateDestroyAPIView[Question]):
    """Retrieve, update, or delete a single question."""

    permission_classes = (QuestionPermission,)

    @override
    def get_queryset(self) -> QuerySet[Question]:
        token = self.request.auth
        user_id = TokenService.get_user_id(token=token)
        is_staff = TokenService.is_staff(token=token)
        return QuestionService.get(user_id=user_id, is_staff=is_staff)

    @override
    def get_serializer_class(self) -> type[BaseSerializer[Question]]:
        if self.request.method in ("PUT", "PATCH"):
            return QuestionWriteSerializer
        return QuestionDetailSerializer


@final
class OptionCreateView(CreateAPIView[AnswerOption]):
    """Attach a new option to a question on a draft questionnaire."""

    serializer_class = OptionCreateSerializer
    permission_classes = (OptionPermission,)

    @override
    def perform_create(self, serializer: BaseSerializer[AnswerOption]) -> None:
        question = serializer.validated_data["question"]
        token = self.request.auth
        assert_draft_owned(questionnaire=question.questionnaire, token=token)  # type: ignore[arg-type]
        serializer.save()


@final
class OptionDetailView(RetrieveUpdateDestroyAPIView[AnswerOption]):
    """Retrieve, update, or delete a single answer option."""

    permission_classes = (OptionPermission,)

    @override
    def get_queryset(self) -> QuerySet[AnswerOption]:
        token = self.request.auth
        user_id = TokenService.get_user_id(token=token)
        is_staff = TokenService.is_staff(token=token)
        return AnswerOptionService.get(user_id=user_id, is_staff=is_staff)

    @override
    def get_serializer_class(self) -> type[BaseSerializer[AnswerOption]]:
        if self.request.method in ("PUT", "PATCH"):
            return OptionWriteSerializer
        return OptionDetailSerializer
