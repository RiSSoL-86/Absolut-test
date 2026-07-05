import pytest

from apps.questionnaires.services import QuestionnaireService
from apps.questionnaires.tests.factories import QuestionnaireFactory
from apps.questions.tests.factories import (
    AnswerOptionFactory,
    QuestionFactory,
)
from apps.users.choices import Role
from apps.users.tests.factories import StaffUserFactory, UserFactory


@pytest.mark.django_db
class TestCreate:
    def test_starts_unpublished_with_empty_order(self) -> None:
        author = UserFactory(role=Role.AUTHOR)

        questionnaire = QuestionnaireService.create(
            author_id=author.id, title="Veggies"
        )

        assert questionnaire.is_published is False
        assert questionnaire.question_order == []


@pytest.mark.django_db
class TestPublish:
    def test_marks_the_questionnaire_published(self) -> None:
        questionnaire = QuestionnaireFactory(is_published=False)

        QuestionnaireService.publish(questionnaire=questionnaire)

        questionnaire.refresh_from_db()
        assert questionnaire.is_published is True


@pytest.mark.django_db
class TestIsPublishable:
    def test_false_without_questions(self) -> None:
        questionnaire = QuestionnaireFactory(is_published=False)

        assert (
            QuestionnaireService.is_publishable(questionnaire=questionnaire)
            is False
        )

    def test_false_when_a_question_has_no_options(self) -> None:
        questionnaire = QuestionnaireFactory(is_published=False)
        QuestionFactory(questionnaire=questionnaire)

        assert (
            QuestionnaireService.is_publishable(questionnaire=questionnaire)
            is False
        )

    def test_true_when_every_question_has_options(self) -> None:
        questionnaire = QuestionnaireFactory(is_published=False)
        question = QuestionFactory(questionnaire=questionnaire)
        AnswerOptionFactory(question=question)

        assert (
            QuestionnaireService.is_publishable(questionnaire=questionnaire)
            is True
        )


@pytest.mark.django_db
class TestVisibility:
    def test_non_staff_sees_published_and_own_drafts_only(self) -> None:
        author = UserFactory(role=Role.AUTHOR)
        published = QuestionnaireFactory(is_published=True)
        own_draft = QuestionnaireFactory(author=author, is_published=False)
        foreign_draft = QuestionnaireFactory(is_published=False)

        visible = QuestionnaireService.get_all(
            user_id=author.id, is_staff=False
        )

        ids = set(visible.values_list("id", flat=True))
        assert {published.id, own_draft.id} <= ids
        assert foreign_draft.id not in ids

    def test_staff_sees_every_questionnaire(self) -> None:
        staff = StaffUserFactory()
        published = QuestionnaireFactory(is_published=True)
        draft = QuestionnaireFactory(is_published=False)

        visible = QuestionnaireService.get_all(user_id=staff.id, is_staff=True)

        ids = set(visible.values_list("id", flat=True))
        assert {published.id, draft.id} <= ids
