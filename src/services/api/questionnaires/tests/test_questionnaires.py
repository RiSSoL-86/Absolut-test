from typing import TYPE_CHECKING

import pytest
from rest_framework.test import APIClient

from apps.questionnaires.models import Questionnaire
from apps.questionnaires.tests.factories import QuestionnaireFactory
from apps.questions.tests.factories import (
    AnswerOptionFactory,
    QuestionFactory,
)
from apps.users.choices import Role
from apps.users.tests.factories import UserFactory
from conftest import authenticate

if TYPE_CHECKING:
    from apps.users.models import User

LIST_URL = "/api/questionnaires/"


def detail_url(pk: object) -> str:
    return f"{LIST_URL}{pk}/"


def publish_url(pk: object) -> str:
    return f"{LIST_URL}{pk}/publish/"


def foreign_author_client() -> APIClient:
    """A client authenticated as some other author."""
    return authenticate(APIClient(), UserFactory(role=Role.AUTHOR))


@pytest.mark.django_db
class TestFeedVisibility:
    def test_anonymous_is_unauthorized(self, api_client: APIClient) -> None:
        assert api_client.get(LIST_URL).status_code == 401

    def test_reader_sees_only_published(self, auth_client: APIClient) -> None:
        published = QuestionnaireFactory(is_published=True)
        draft = QuestionnaireFactory(is_published=False)

        rows = auth_client.get(LIST_URL).json()["results"]

        ids = {row["id"] for row in rows}
        assert str(published.id) in ids
        assert str(draft.id) not in ids

    def test_author_also_sees_own_drafts(
        self, author_client: APIClient, author_user: User
    ) -> None:
        own_draft = QuestionnaireFactory(
            author=author_user, is_published=False
        )
        foreign_draft = QuestionnaireFactory(is_published=False)

        ids = {
            row["id"] for row in author_client.get(LIST_URL).json()["results"]
        }
        assert str(own_draft.id) in ids
        assert str(foreign_draft.id) not in ids

    def test_staff_sees_foreign_drafts(self, staff_client: APIClient) -> None:
        draft = QuestionnaireFactory(is_published=False)

        ids = {
            row["id"] for row in staff_client.get(LIST_URL).json()["results"]
        }
        assert str(draft.id) in ids


@pytest.mark.django_db
class TestCreate:
    def test_author_creates_an_unpublished_questionnaire(
        self, author_client: APIClient, author_user: User
    ) -> None:
        response = author_client.post(
            LIST_URL, {"title": "Veggies"}, format="json"
        )

        assert response.status_code == 201
        created = Questionnaire.objects.get(id=response.json()["id"])
        assert created.author_id == author_user.id
        assert created.is_published is False

    def test_question_order_cannot_be_set_on_create(
        self, author_client: APIClient
    ) -> None:
        response = author_client.post(
            LIST_URL,
            {"title": "Veggies", "question_order": ["ignored"]},
            format="json",
        )

        assert response.status_code == 201
        created = Questionnaire.objects.get(id=response.json()["id"])
        assert created.question_order == []

    def test_reader_cannot_create(self, auth_client: APIClient) -> None:
        response = auth_client.post(
            LIST_URL, {"title": "Veggies"}, format="json"
        )

        assert response.status_code == 403

    def test_anonymous_cannot_create(self, api_client: APIClient) -> None:
        response = api_client.post(
            LIST_URL, {"title": "Veggies"}, format="json"
        )

        assert response.status_code == 401


@pytest.mark.django_db
class TestDetail:
    def test_nests_questions_and_options_in_author_order(
        self, auth_client: APIClient
    ) -> None:
        questionnaire = QuestionnaireFactory(is_published=True)
        first = QuestionFactory(questionnaire=questionnaire)
        second = QuestionFactory(questionnaire=questionnaire)
        questionnaire.question_order = [second.id, first.id]
        questionnaire.save(update_fields=["question_order"])
        left = AnswerOptionFactory(question=second)
        right = AnswerOptionFactory(question=second)
        second.option_order = [right.id, left.id]
        second.save(update_fields=["option_order"])

        body = auth_client.get(detail_url(questionnaire.id)).json()

        questions = body["questions"]
        assert [q["id"] for q in questions] == [
            str(second.id),
            str(first.id),
        ]
        assert [o["id"] for o in questions[0]["options"]] == [
            str(right.id),
            str(left.id),
        ]

    def test_reader_cannot_open_a_foreign_draft(
        self, auth_client: APIClient
    ) -> None:
        draft = QuestionnaireFactory(is_published=False)

        response = auth_client.get(detail_url(draft.id))

        assert response.status_code == 404

    def test_author_opens_own_draft(
        self, author_client: APIClient, author_user: User
    ) -> None:
        draft = QuestionnaireFactory(author=author_user, is_published=False)

        response = author_client.get(detail_url(draft.id))

        assert response.status_code == 200


@pytest.mark.django_db
class TestUpdate:
    def test_author_reorders_questions(
        self, author_client: APIClient, author_user: User
    ) -> None:
        draft = QuestionnaireFactory(author=author_user, is_published=False)
        first = QuestionFactory(questionnaire=draft)
        second = QuestionFactory(questionnaire=draft)

        response = author_client.patch(
            detail_url(draft.id),
            {"question_order": [str(second.id), str(first.id)]},
            format="json",
        )

        assert response.status_code == 200
        assert response.json()["question_order"] == [
            str(second.id),
            str(first.id),
        ]
        draft.refresh_from_db()
        assert draft.question_order == [second.id, first.id]

    def test_reorder_rejects_a_missing_question(
        self, author_client: APIClient, author_user: User
    ) -> None:
        draft = QuestionnaireFactory(author=author_user, is_published=False)
        first = QuestionFactory(questionnaire=draft)
        QuestionFactory(questionnaire=draft)

        response = author_client.patch(
            detail_url(draft.id),
            {"question_order": [str(first.id)]},
            format="json",
        )

        assert response.status_code == 400

    def test_reorder_rejects_a_duplicate(
        self, author_client: APIClient, author_user: User
    ) -> None:
        draft = QuestionnaireFactory(author=author_user, is_published=False)
        first = QuestionFactory(questionnaire=draft)
        QuestionFactory(questionnaire=draft)

        response = author_client.patch(
            detail_url(draft.id),
            {"question_order": [str(first.id), str(first.id)]},
            format="json",
        )

        assert response.status_code == 400

    def test_author_cannot_update_a_foreign_draft(
        self, author_client: APIClient
    ) -> None:
        draft = QuestionnaireFactory(is_published=False)

        response = author_client.patch(
            detail_url(draft.id), {"title": "Hijacked"}, format="json"
        )

        assert response.status_code == 404

    def test_nobody_can_update_a_published_questionnaire(
        self, author_client: APIClient, author_user: User
    ) -> None:
        published = QuestionnaireFactory(author=author_user, is_published=True)

        response = author_client.patch(
            detail_url(published.id), {"title": "New"}, format="json"
        )

        assert response.status_code == 403


@pytest.mark.django_db
class TestPublish:
    def _ready_draft(self, author: User) -> Questionnaire:
        draft = QuestionnaireFactory(author=author, is_published=False)
        question = QuestionFactory(questionnaire=draft)
        AnswerOptionFactory(question=question)
        return draft

    def test_author_publishes_a_ready_draft(
        self, author_client: APIClient, author_user: User
    ) -> None:
        draft = self._ready_draft(author_user)

        response = author_client.post(publish_url(draft.id))

        assert response.status_code == 200
        assert response.json()["is_published"] is True
        draft.refresh_from_db()
        assert draft.is_published is True

    def test_empty_questionnaire_is_rejected(
        self, author_client: APIClient, author_user: User
    ) -> None:
        draft = QuestionnaireFactory(author=author_user, is_published=False)

        response = author_client.post(publish_url(draft.id))

        assert response.status_code == 400
        draft.refresh_from_db()
        assert draft.is_published is False

    def test_question_without_options_is_rejected(
        self, author_client: APIClient, author_user: User
    ) -> None:
        draft = QuestionnaireFactory(author=author_user, is_published=False)
        QuestionFactory(questionnaire=draft)

        response = author_client.post(publish_url(draft.id))

        assert response.status_code == 400

    def test_reader_cannot_publish(self, auth_client: APIClient) -> None:
        draft = QuestionnaireFactory(is_published=False)

        assert auth_client.post(publish_url(draft.id)).status_code == 403

    def test_author_cannot_publish_a_foreign_draft(
        self, author_client: APIClient
    ) -> None:
        draft = QuestionnaireFactory(is_published=False)

        assert author_client.post(publish_url(draft.id)).status_code == 404

    def test_republishing_is_rejected(
        self, author_client: APIClient, author_user: User
    ) -> None:
        published = QuestionnaireFactory(author=author_user, is_published=True)

        assert author_client.post(publish_url(published.id)).status_code == 403


@pytest.mark.django_db
class TestDelete:
    def test_author_deletes_own_draft(
        self, author_client: APIClient, author_user: User
    ) -> None:
        draft = QuestionnaireFactory(author=author_user, is_published=False)

        response = author_client.delete(detail_url(draft.id))

        assert response.status_code == 204
        assert not Questionnaire.objects.filter(id=draft.id).exists()

    def test_cannot_delete_a_published_questionnaire(
        self, author_client: APIClient, author_user: User
    ) -> None:
        published = QuestionnaireFactory(author=author_user, is_published=True)

        response = author_client.delete(detail_url(published.id))

        assert response.status_code == 403
