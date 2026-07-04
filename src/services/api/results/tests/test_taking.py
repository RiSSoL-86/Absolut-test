from typing import TYPE_CHECKING

import pytest

from apps.questionnaires.tests.factories import QuestionnaireFactory
from apps.questions.tests.factories import (
    AnswerOptionFactory,
    QuestionFactory,
)
from apps.results.models import SurveyAnswer, SurveyResult

if TYPE_CHECKING:
    from rest_framework.test import APIClient

    from apps.questionnaires.models import Questionnaire
    from apps.questions.models import Question
    from apps.users.models import User


def next_url(pk: object) -> str:
    return f"/api/questionnaires/{pk}/next-question/"


def answers_url(pk: object) -> str:
    return f"/api/questionnaires/{pk}/answers/"


def two_question_survey() -> tuple[Questionnaire, Question, Question]:
    """A published survey with two single-choice questions (two options)."""
    questionnaire = QuestionnaireFactory(is_published=True)
    first = QuestionFactory(questionnaire=questionnaire)
    AnswerOptionFactory(question=first)
    AnswerOptionFactory(question=first)
    second = QuestionFactory(questionnaire=questionnaire)
    AnswerOptionFactory(question=second)
    AnswerOptionFactory(question=second)
    return questionnaire, first, second


def answer(question: Question, *options: object) -> dict[str, object]:
    return {"question": str(question.id), "options": [str(o) for o in options]}


@pytest.mark.django_db
class TestNextQuestion:
    def test_returns_the_first_unanswered_question_with_options(
        self, auth_client: APIClient
    ) -> None:
        questionnaire, first, _ = two_question_survey()

        body = auth_client.get(next_url(questionnaire.id)).json()

        assert body["id"] == str(first.id)
        assert len(body["options"]) == 2

    def test_anonymous_is_unauthorized(self, api_client: APIClient) -> None:
        questionnaire, _, _ = two_question_survey()

        response = api_client.get(next_url(questionnaire.id))

        assert response.status_code == 401

    def test_unpublished_survey_is_not_found(
        self, auth_client: APIClient
    ) -> None:
        draft = QuestionnaireFactory(is_published=False)

        assert auth_client.get(next_url(draft.id)).status_code == 404

    def test_no_content_once_every_question_is_answered(
        self, auth_client: APIClient, user: User
    ) -> None:
        questionnaire, first, second = two_question_survey()
        result = SurveyResult.objects.create(
            questionnaire=questionnaire, respondent=user
        )
        SurveyAnswer.objects.create(
            result=result, question=first, option=first.options.first()
        )
        SurveyAnswer.objects.create(
            result=result, question=second, option=second.options.first()
        )

        assert auth_client.get(next_url(questionnaire.id)).status_code == 204


@pytest.mark.django_db
class TestAnswers:
    def test_progressive_answering_advances_then_completes(
        self, auth_client: APIClient, user: User
    ) -> None:
        questionnaire, first, second = two_question_survey()

        step = auth_client.post(
            answers_url(questionnaire.id),
            {"answers": [answer(first, first.options.first().id)]},
            format="json",
        ).json()
        assert step["completed"] is False
        assert step["next_question"]["id"] == str(second.id)

        final = auth_client.post(
            answers_url(questionnaire.id),
            {"answers": [answer(second, second.options.first().id)]},
            format="json",
        ).json()
        assert final["completed"] is True
        assert final["next_question"] is None

        result = SurveyResult.objects.get(
            questionnaire=questionnaire, respondent=user
        )
        assert result.completed_timestamp is not None
        assert result.answers.count() == 2

    def test_whole_set_in_one_request_completes(
        self, auth_client: APIClient
    ) -> None:
        questionnaire, first, second = two_question_survey()

        body = auth_client.post(
            answers_url(questionnaire.id),
            {
                "answers": [
                    answer(first, first.options.first().id),
                    answer(second, second.options.first().id),
                ]
            },
            format="json",
        ).json()

        assert body["completed"] is True
        assert body["next_question"] is None

    def test_foreign_question_is_rejected(
        self, auth_client: APIClient
    ) -> None:
        questionnaire, _, _ = two_question_survey()
        stray = QuestionFactory()
        option = AnswerOptionFactory(question=stray)

        response = auth_client.post(
            answers_url(questionnaire.id),
            {"answers": [answer(stray, option.id)]},
            format="json",
        )

        assert response.status_code == 400

    def test_option_of_another_question_is_rejected(
        self, auth_client: APIClient
    ) -> None:
        questionnaire, first, second = two_question_survey()

        response = auth_client.post(
            answers_url(questionnaire.id),
            {"answers": [answer(first, second.options.first().id)]},
            format="json",
        )

        assert response.status_code == 400

    def test_single_choice_rejects_two_options(
        self, auth_client: APIClient
    ) -> None:
        questionnaire, first, _ = two_question_survey()
        options = list(first.options.all())

        response = auth_client.post(
            answers_url(questionnaire.id),
            {"answers": [answer(first, options[0].id, options[1].id)]},
            format="json",
        )

        assert response.status_code == 400

    def test_answering_the_same_question_twice_is_rejected(
        self, auth_client: APIClient
    ) -> None:
        questionnaire, first, _ = two_question_survey()
        auth_client.post(
            answers_url(questionnaire.id),
            {"answers": [answer(first, first.options.first().id)]},
            format="json",
        )

        response = auth_client.post(
            answers_url(questionnaire.id),
            {"answers": [answer(first, first.options.last().id)]},
            format="json",
        )

        assert response.status_code == 400
