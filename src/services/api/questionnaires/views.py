from typing import TYPE_CHECKING, final, override

from rest_framework.exceptions import ValidationError
from rest_framework.generics import (
    GenericAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.response import Response

from apps.questionnaires.models import Questionnaire
from apps.questionnaires.services import QuestionnaireService
from services.api.questionnaires.permissions import QuestionnairePermission
from services.api.questionnaires.serializers import (
    QuestionnaireCreateSerializer,
    QuestionnaireDetailSerializer,
    QuestionnaireListSerializer,
    QuestionnaireWriteSerializer,
)
from services.jwt_extensions.services import TokenService

if TYPE_CHECKING:
    from uuid import UUID

    from django.db.models import QuerySet
    from rest_framework.request import Request
    from rest_framework.serializers import BaseSerializer


@final
class QuestionnaireListCreateView(ListCreateAPIView[Questionnaire]):
    """List the visible feed, or create a questionnaire as its author."""

    permission_classes = (QuestionnairePermission,)

    @override
    def get_queryset(self) -> QuerySet[Questionnaire]:
        token = self.request.auth
        user_id = TokenService.get_user_id(token=token)
        is_staff = TokenService.is_staff(token=token)
        return QuestionnaireService.get_all(user_id=user_id, is_staff=is_staff)

    @override
    def get_serializer_class(self) -> type[BaseSerializer[Questionnaire]]:
        if self.request.method == "POST":
            return QuestionnaireCreateSerializer
        return QuestionnaireListSerializer

    @override
    def perform_create(
        self, serializer: BaseSerializer[Questionnaire]
    ) -> None:
        token = self.request.auth
        user_id = TokenService.get_user_id(token=token)
        serializer.save(author_id=user_id)


@final
class QuestionnaireDetailView(RetrieveUpdateDestroyAPIView[Questionnaire]):
    """Retrieve, update, or delete a single questionnaire."""

    permission_classes = (QuestionnairePermission,)

    @override
    def get_queryset(self) -> QuerySet[Questionnaire]:
        token = self.request.auth
        user_id = TokenService.get_user_id(token=token)
        is_staff = TokenService.is_staff(token=token)
        return QuestionnaireService.get(user_id=user_id, is_staff=is_staff)

    @override
    def get_serializer_class(self) -> type[BaseSerializer[Questionnaire]]:
        if self.request.method in ("PUT", "PATCH"):
            return QuestionnaireWriteSerializer
        return QuestionnaireDetailSerializer


@final
class QuestionnairePublishView(GenericAPIView[Questionnaire]):
    """Publish a questionnaire, freezing it for respondents."""

    permission_classes = (QuestionnairePermission,)
    serializer_class = QuestionnaireDetailSerializer

    @override
    def get_queryset(self) -> QuerySet[Questionnaire]:
        token = self.request.auth
        user_id = TokenService.get_user_id(token=token)
        is_staff = TokenService.is_staff(token=token)
        return QuestionnaireService.get(user_id=user_id, is_staff=is_staff)

    def post(self, request: Request, pk: UUID) -> Response:
        questionnaire = self.get_object()
        if not QuestionnaireService.is_publishable(
            questionnaire=questionnaire
        ):
            raise ValidationError(
                "Add questions with options before publishing."
            )
        QuestionnaireService.publish(questionnaire=questionnaire)
        return Response(self.get_serializer(questionnaire).data)
