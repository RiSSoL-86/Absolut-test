from typing import TYPE_CHECKING

import pytest

from apps.questionnaires.tests.factories import QuestionnaireFactory
from apps.questions.models import Question
from apps.questions.tests.factories import (
    AnswerOptionFactory,
    QuestionFactory,
)

if TYPE_CHECKING:
    from rest_framework.test import APIClient

    from apps.questionnaires.models import Questionnaire
    from apps.users.models import User

LIST_URL = "/api/questions/"


def detail_url(pk: object) -> str:
    return f"{LIST_URL}{pk}/"


def draft_owned_by(author: User) -> Questionnaire:
    return QuestionnaireFactory(author=author, is_published=False)


@pytest.mark.django_db
class TestCreate:
    def test_author_adds_a_question_to_own_draft(
        self, author_client: APIClient, author_user: User
    ) -> None:
        draft = draft_owned_by(author_user)

        response = author_client.post(
            LIST_URL,
            {"questionnaire": str(draft.id), "text": "Cucumbers?"},
            format="json",
        )

        assert response.status_code == 201
        question = Question.objects.get(id=response.json()["id"])
        assert question.questionnaire_id == draft.id
        draft.refresh_from_db()
        assert draft.question_order == [question.id]

    def test_cannot_add_to_a_foreign_questionnaire(
        self, author_client: APIClient
    ) -> None:
        foreign = QuestionnaireFactory(is_published=False)

        response = author_client.post(
            LIST_URL,
            {"questionnaire": str(foreign.id), "text": "Cucumbers?"},
            format="json",
        )

        assert response.status_code == 403

    def test_cannot_add_to_a_published_questionnaire(
        self, author_client: APIClient, author_user: User
    ) -> None:
        published = QuestionnaireFactory(author=author_user, is_published=True)

        response = author_client.post(
            LIST_URL,
            {"questionnaire": str(published.id), "text": "Cucumbers?"},
            format="json",
        )

        assert response.status_code == 403

    def test_reader_cannot_create(self, auth_client: APIClient) -> None:
        draft = QuestionnaireFactory(is_published=False)

        response = auth_client.post(
            LIST_URL,
            {"questionnaire": str(draft.id), "text": "Cucumbers?"},
            format="json",
        )

        assert response.status_code == 403


@pytest.mark.django_db
class TestDetail:
    def test_shows_options_in_author_order(
        self, auth_client: APIClient
    ) -> None:
        question = QuestionFactory(
            questionnaire=QuestionnaireFactory(is_published=True)
        )
        left = AnswerOptionFactory(question=question)
        right = AnswerOptionFactory(question=question)
        question.option_order = [right.id, left.id]
        question.save(update_fields=["option_order"])

        body = auth_client.get(detail_url(question.id)).json()

        assert [o["id"] for o in body["options"]] == [
            str(right.id),
            str(left.id),
        ]

    def test_reader_cannot_open_a_question_of_a_foreign_draft(
        self, auth_client: APIClient
    ) -> None:
        question = QuestionFactory(
            questionnaire=QuestionnaireFactory(is_published=False)
        )

        assert auth_client.get(detail_url(question.id)).status_code == 404


@pytest.mark.django_db
class TestUpdate:
    def test_author_reorders_options(
        self, author_client: APIClient, author_user: User
    ) -> None:
        question = QuestionFactory(questionnaire=draft_owned_by(author_user))
        left = AnswerOptionFactory(question=question)
        right = AnswerOptionFactory(question=question)

        response = author_client.patch(
            detail_url(question.id),
            {"option_order": [str(right.id), str(left.id)]},
            format="json",
        )

        assert response.status_code == 200
        assert response.json()["option_order"] == [
            str(right.id),
            str(left.id),
        ]

    def test_reorder_rejects_a_bad_set(
        self, author_client: APIClient, author_user: User
    ) -> None:
        question = QuestionFactory(questionnaire=draft_owned_by(author_user))
        left = AnswerOptionFactory(question=question)
        AnswerOptionFactory(question=question)

        response = author_client.patch(
            detail_url(question.id),
            {"option_order": [str(left.id)]},
            format="json",
        )

        assert response.status_code == 400

    def test_questionnaire_cannot_be_changed(
        self, author_client: APIClient, author_user: User
    ) -> None:
        origin = draft_owned_by(author_user)
        question = QuestionFactory(questionnaire=origin)
        elsewhere = draft_owned_by(author_user)

        response = author_client.patch(
            detail_url(question.id),
            {"questionnaire": str(elsewhere.id), "text": "Moved?"},
            format="json",
        )

        assert response.status_code == 200
        question.refresh_from_db()
        assert question.questionnaire_id == origin.id
        assert question.text == "Moved?"

    def test_cannot_update_a_question_of_a_published_questionnaire(
        self, author_client: APIClient, author_user: User
    ) -> None:
        question = QuestionFactory(
            questionnaire=QuestionnaireFactory(
                author=author_user, is_published=True
            )
        )

        response = author_client.patch(
            detail_url(question.id), {"text": "New?"}, format="json"
        )

        assert response.status_code == 403

    def test_cannot_update_a_foreign_question(
        self, author_client: APIClient
    ) -> None:
        question = QuestionFactory(
            questionnaire=QuestionnaireFactory(is_published=False)
        )

        response = author_client.patch(
            detail_url(question.id), {"text": "New?"}, format="json"
        )

        assert response.status_code == 404


@pytest.mark.django_db
class TestDelete:
    def test_delete_drops_the_question_from_the_order(
        self, author_client: APIClient, author_user: User
    ) -> None:
        draft = draft_owned_by(author_user)
        first = QuestionFactory(questionnaire=draft)
        second = QuestionFactory(questionnaire=draft)

        response = author_client.delete(detail_url(first.id))

        assert response.status_code == 204
        draft.refresh_from_db()
        assert draft.question_order == [second.id]

    def test_cannot_delete_from_a_published_questionnaire(
        self, author_client: APIClient, author_user: User
    ) -> None:
        question = QuestionFactory(
            questionnaire=QuestionnaireFactory(
                author=author_user, is_published=True
            )
        )

        assert author_client.delete(detail_url(question.id)).status_code == 403
