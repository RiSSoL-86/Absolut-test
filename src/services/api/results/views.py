from typing import TYPE_CHECKING, final

from drf_spectacular.utils import extend_schema
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.questionnaires.models import Questionnaire
from apps.results.services import SurveyResultService
from services.api.questions.serializers import NestedQuestionSerializer
from services.api.results.permissions import StatsPermission
from services.api.results.serializers import (
    AnswersSerializer,
    StatsSerializer,
)
from services.jwt_extensions.services import TokenService

if TYPE_CHECKING:
    from uuid import UUID

    from rest_framework.request import Request


@final
class NextQuestionView(GenericAPIView[Questionnaire]):
    """The next question the respondent must answer in this survey."""

    queryset = Questionnaire.objects.filter(is_published=True)
    serializer_class = NestedQuestionSerializer  # type: ignore[assignment]
    permission_classes = (IsAuthenticated,)

    def get(self, request: Request, pk: UUID) -> Response:
        token = request.auth
        questionnaire = self.get_object()
        user_id = TokenService.get_user_id(token=token)
        question = SurveyResultService.next_question(
            questionnaire=questionnaire, respondent_id=user_id
        )
        if question is None:
            return Response(status=204)
        return Response(NestedQuestionSerializer(question).data)


@final
class AnswersView(GenericAPIView[Questionnaire]):
    """Submit one or many answers; the result completes when all are in."""

    queryset = Questionnaire.objects.filter(is_published=True)
    serializer_class = AnswersSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request: Request, pk: UUID) -> Response:
        token = request.auth
        questionnaire = self.get_object()
        user_id = TokenService.get_user_id(token=token)

        serializer = self.get_serializer(
            data=request.data,
            context={"questionnaire": questionnaire, "respondent_id": user_id},
        )
        serializer.is_valid(raise_exception=True)
        result = SurveyResultService.submit(
            questionnaire=questionnaire,
            respondent_id=user_id,
            answers=serializer.validated_data["answers"],
        )

        following = SurveyResultService.next_question(
            questionnaire=questionnaire, respondent_id=user_id
        )
        return Response(
            {
                "completed": result.completed_timestamp is not None,
                "next_question": (
                    NestedQuestionSerializer(following).data
                    if following is not None
                    else None
                ),
            }
        )


@final
class StatsView(GenericAPIView[Questionnaire]):
    """Response counts, popular options and average completion time."""

    queryset = Questionnaire.objects.filter(is_published=True)
    serializer_class = StatsSerializer
    permission_classes = (IsAuthenticated, StatsPermission)

    @extend_schema(responses=StatsSerializer)
    def get(self, request: Request, pk: UUID) -> Response:
        questionnaire = self.get_object()
        return Response(SurveyResultService.stats(questionnaire=questionnaire))
