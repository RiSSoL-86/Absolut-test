from typing import TYPE_CHECKING

import pytest

from apps.questionnaires.tests.factories import QuestionnaireFactory
from apps.questions.tests.factories import (
    AnswerOptionFactory,
    QuestionFactory,
)
from apps.results.services import SurveyResultService
from apps.users.choices import Role
from apps.users.tests.factories import UserFactory

if TYPE_CHECKING:
    from rest_framework.test import APIClient

    from apps.questionnaires.models import Questionnaire
    from apps.users.models import User


def stats_url(pk: object) -> str:
    return f"/api/questionnaires/{pk}/stats/"


def answered_survey(author: User) -> Questionnaire:
    """A published survey owned by ``author`` with one recorded answer."""
    questionnaire = QuestionnaireFactory(author=author, is_published=True)
    question = QuestionFactory(questionnaire=questionnaire)
    option = AnswerOptionFactory(question=question)
    questionnaire.refresh_from_db()
    respondent = UserFactory()
    SurveyResultService.submit(
        questionnaire=questionnaire,
        respondent_id=respondent.id,
        answers=[{"question": question.id, "options": [option.id]}],
    )
    return questionnaire


@pytest.mark.django_db
class TestStats:
    def test_author_reads_own_survey_stats(
        self, author_client: APIClient, author_user: User
    ) -> None:
        questionnaire = answered_survey(author_user)

        body = author_client.get(stats_url(questionnaire.id)).json()

        assert body["responses"] == 1
        assert body["completed"] == 1
        assert body["questions"][0]["options"][0]["count"] == 1

    def test_reader_is_forbidden(
        self, auth_client: APIClient, author_user: User
    ) -> None:
        questionnaire = answered_survey(author_user)

        assert auth_client.get(stats_url(questionnaire.id)).status_code == 403

    def test_foreign_author_is_forbidden(
        self, author_client: APIClient
    ) -> None:
        questionnaire = answered_survey(UserFactory(role=Role.AUTHOR))

        response = author_client.get(stats_url(questionnaire.id))

        assert response.status_code == 403

    def test_anonymous_is_unauthorized(
        self, api_client: APIClient, author_user: User
    ) -> None:
        questionnaire = answered_survey(author_user)

        assert api_client.get(stats_url(questionnaire.id)).status_code == 401
