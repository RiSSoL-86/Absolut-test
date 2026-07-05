import pytest

from apps.questionnaires.tests.factories import QuestionnaireFactory
from apps.questions.services import AnswerOptionService, QuestionService
from apps.questions.tests.factories import (
    AnswerOptionFactory,
    QuestionFactory,
)
from apps.users.choices import Role
from apps.users.tests.factories import UserFactory


@pytest.mark.django_db
class TestQuestionCreate:
    def test_creates_a_question_inside_the_questionnaire(self) -> None:
        questionnaire = QuestionnaireFactory(is_published=False)

        question = QuestionService.create(
            questionnaire=questionnaire, text="Cucumbers?"
        )

        assert question.questionnaire_id == questionnaire.id
        assert question.allow_multiple is False


@pytest.mark.django_db
class TestQuestionVisibility:
    def test_non_staff_sees_questions_of_published_and_own(self) -> None:
        author = UserFactory(role=Role.AUTHOR)
        published = QuestionFactory(
            questionnaire=QuestionnaireFactory(is_published=True)
        )
        own = QuestionFactory(
            questionnaire=QuestionnaireFactory(
                author=author, is_published=False
            )
        )
        foreign = QuestionFactory(
            questionnaire=QuestionnaireFactory(is_published=False)
        )

        visible = QuestionService.get(user_id=author.id, is_staff=False)

        ids = set(visible.values_list("id", flat=True))
        assert {published.id, own.id} <= ids
        assert foreign.id not in ids


@pytest.mark.django_db
class TestOptionService:
    def test_create_then_update_changes_only_text(self) -> None:
        question = QuestionFactory(
            questionnaire=QuestionnaireFactory(is_published=False)
        )

        option = AnswerOptionService.create(question=question, text="Yes")
        AnswerOptionService.update(option=option, fields={"text": "Nope"})

        option.refresh_from_db()
        assert option.question_id == question.id
        assert option.text == "Nope"

    def test_non_staff_sees_options_of_published_and_own(self) -> None:
        author = UserFactory(role=Role.AUTHOR)
        published = AnswerOptionFactory(
            question=QuestionFactory(
                questionnaire=QuestionnaireFactory(is_published=True)
            )
        )
        foreign = AnswerOptionFactory(
            question=QuestionFactory(
                questionnaire=QuestionnaireFactory(is_published=False)
            )
        )

        visible = AnswerOptionService.get(user_id=author.id, is_staff=False)

        ids = set(visible.values_list("id", flat=True))
        assert published.id in ids
        assert foreign.id not in ids
