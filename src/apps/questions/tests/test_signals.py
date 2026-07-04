import pytest

from apps.questionnaires.tests.factories import QuestionnaireFactory
from apps.questions.tests.factories import (
    AnswerOptionFactory,
    QuestionFactory,
)


@pytest.mark.django_db
class TestQuestionOrder:
    def test_creating_questions_appends_them_to_survey_order(self) -> None:
        questionnaire = QuestionnaireFactory()

        first = QuestionFactory(questionnaire=questionnaire)
        second = QuestionFactory(questionnaire=questionnaire)

        questionnaire.refresh_from_db()
        assert questionnaire.question_order == [first.pk, second.pk]

    def test_deleting_a_question_drops_it_from_the_order(self) -> None:
        questionnaire = QuestionnaireFactory()
        first = QuestionFactory(questionnaire=questionnaire)
        second = QuestionFactory(questionnaire=questionnaire)

        first.delete()

        questionnaire.refresh_from_db()
        assert questionnaire.question_order == [second.pk]


@pytest.mark.django_db
class TestOptionOrder:
    def test_creating_options_appends_them_to_question_order(self) -> None:
        question = QuestionFactory()

        first = AnswerOptionFactory(question=question)
        second = AnswerOptionFactory(question=question)

        question.refresh_from_db()
        assert question.option_order == [first.pk, second.pk]

    def test_deleting_an_option_drops_it_from_the_order(self) -> None:
        question = QuestionFactory()
        first = AnswerOptionFactory(question=question)
        second = AnswerOptionFactory(question=question)

        first.delete()

        question.refresh_from_db()
        assert question.option_order == [second.pk]
