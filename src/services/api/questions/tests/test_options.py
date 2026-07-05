from typing import TYPE_CHECKING

import pytest

from apps.questionnaires.tests.factories import QuestionnaireFactory
from apps.questions.models import AnswerOption
from apps.questions.tests.factories import (
    AnswerOptionFactory,
    QuestionFactory,
)

if TYPE_CHECKING:
    from rest_framework.test import APIClient

    from apps.questions.models import Question
    from apps.users.models import User

LIST_URL = "/api/questions/options/"


def detail_url(pk: object) -> str:
    return f"{LIST_URL}{pk}/"


def draft_question_owned_by(author: User) -> Question:
    return QuestionFactory(
        questionnaire=QuestionnaireFactory(author=author, is_published=False)
    )


@pytest.mark.django_db
class TestCreate:
    def test_author_adds_an_option_to_own_draft_question(
        self, author_client: APIClient, author_user: User
    ) -> None:
        question = draft_question_owned_by(author_user)

        response = author_client.post(
            LIST_URL,
            {"question": str(question.id), "text": "Yes"},
            format="json",
        )

        assert response.status_code == 201
        option = AnswerOption.objects.get(id=response.json()["id"])
        question.refresh_from_db()
        assert question.option_order == [option.id]

    def test_cannot_add_to_a_foreign_question(
        self, author_client: APIClient
    ) -> None:
        question = QuestionFactory(
            questionnaire=QuestionnaireFactory(is_published=False)
        )

        response = author_client.post(
            LIST_URL,
            {"question": str(question.id), "text": "Yes"},
            format="json",
        )

        assert response.status_code == 403

    def test_cannot_add_to_a_published_question(
        self, author_client: APIClient, author_user: User
    ) -> None:
        question = QuestionFactory(
            questionnaire=QuestionnaireFactory(
                author=author_user, is_published=True
            )
        )

        response = author_client.post(
            LIST_URL,
            {"question": str(question.id), "text": "Yes"},
            format="json",
        )

        assert response.status_code == 403

    def test_reader_cannot_create(self, auth_client: APIClient) -> None:
        question = QuestionFactory(
            questionnaire=QuestionnaireFactory(is_published=False)
        )

        response = auth_client.post(
            LIST_URL,
            {"question": str(question.id), "text": "Yes"},
            format="json",
        )

        assert response.status_code == 403


@pytest.mark.django_db
class TestUpdate:
    def test_author_edits_the_text(
        self, author_client: APIClient, author_user: User
    ) -> None:
        option = AnswerOptionFactory(
            question=draft_question_owned_by(author_user)
        )

        response = author_client.patch(
            detail_url(option.id), {"text": "Nope"}, format="json"
        )

        assert response.status_code == 200
        option.refresh_from_db()
        assert option.text == "Nope"

    def test_question_cannot_be_changed(
        self, author_client: APIClient, author_user: User
    ) -> None:
        question = draft_question_owned_by(author_user)
        option = AnswerOptionFactory(question=question)
        elsewhere = draft_question_owned_by(author_user)

        response = author_client.patch(
            detail_url(option.id),
            {"question": str(elsewhere.id), "text": "Moved"},
            format="json",
        )

        assert response.status_code == 200
        option.refresh_from_db()
        assert option.question_id == question.id
        assert option.text == "Moved"

    def test_cannot_update_on_a_published_questionnaire(
        self, author_client: APIClient, author_user: User
    ) -> None:
        option = AnswerOptionFactory(
            question=QuestionFactory(
                questionnaire=QuestionnaireFactory(
                    author=author_user, is_published=True
                )
            )
        )

        response = author_client.patch(
            detail_url(option.id), {"text": "Nope"}, format="json"
        )

        assert response.status_code == 403

    def test_cannot_update_a_foreign_option(
        self, author_client: APIClient
    ) -> None:
        option = AnswerOptionFactory(
            question=QuestionFactory(
                questionnaire=QuestionnaireFactory(is_published=False)
            )
        )

        response = author_client.patch(
            detail_url(option.id), {"text": "Nope"}, format="json"
        )

        assert response.status_code == 404


@pytest.mark.django_db
class TestDelete:
    def test_delete_drops_the_option_from_the_order(
        self, author_client: APIClient, author_user: User
    ) -> None:
        question = draft_question_owned_by(author_user)
        first = AnswerOptionFactory(question=question)
        second = AnswerOptionFactory(question=question)

        response = author_client.delete(detail_url(first.id))

        assert response.status_code == 204
        question.refresh_from_db()
        assert question.option_order == [second.id]

    def test_cannot_delete_on_a_published_questionnaire(
        self, author_client: APIClient, author_user: User
    ) -> None:
        option = AnswerOptionFactory(
            question=QuestionFactory(
                questionnaire=QuestionnaireFactory(
                    author=author_user, is_published=True
                )
            )
        )

        assert author_client.delete(detail_url(option.id)).status_code == 403
