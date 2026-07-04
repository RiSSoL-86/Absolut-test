import pytest

from apps.questionnaires.tests.factories import QuestionnaireFactory
from apps.questions.tests.factories import (
    AnswerOptionFactory,
    QuestionFactory,
)
from apps.results.models import SurveyAnswer
from apps.results.services import SurveyResultService
from apps.results.tests.factories import (
    SurveyAnswerFactory,
    SurveyResultFactory,
)
from apps.users.tests.factories import UserFactory


@pytest.mark.django_db
class TestNextQuestion:
    def test_walks_questions_in_author_order_until_done(self) -> None:
        questionnaire = QuestionnaireFactory(is_published=True)
        first = QuestionFactory(questionnaire=questionnaire)
        first_option = AnswerOptionFactory(question=first)
        second = QuestionFactory(questionnaire=questionnaire)
        second_option = AnswerOptionFactory(question=second)
        respondent = UserFactory()
        questionnaire.refresh_from_db()

        def upcoming() -> object:
            question = SurveyResultService.next_question(
                questionnaire=questionnaire, respondent_id=respondent.id
            )
            return None if question is None else question.id

        assert upcoming() == first.id

        result = SurveyResultFactory(
            questionnaire=questionnaire, respondent=respondent
        )
        SurveyAnswerFactory(result=result, question=first, option=first_option)
        assert upcoming() == second.id

        SurveyAnswerFactory(
            result=result, question=second, option=second_option
        )
        assert upcoming() is None


@pytest.mark.django_db
class TestSubmit:
    def test_completes_only_once_every_question_is_answered(self) -> None:
        questionnaire = QuestionnaireFactory(is_published=True)
        first = QuestionFactory(questionnaire=questionnaire)
        first_option = AnswerOptionFactory(question=first)
        second = QuestionFactory(questionnaire=questionnaire)
        second_option = AnswerOptionFactory(question=second)
        respondent = UserFactory()
        questionnaire.refresh_from_db()

        partial = SurveyResultService.submit(
            questionnaire=questionnaire,
            respondent_id=respondent.id,
            answers=[{"question": first.id, "options": [first_option.id]}],
        )
        assert partial.completed_timestamp is None

        done = SurveyResultService.submit(
            questionnaire=questionnaire,
            respondent_id=respondent.id,
            answers=[{"question": second.id, "options": [second_option.id]}],
        )
        assert done.completed_timestamp is not None
        assert SurveyAnswer.objects.filter(result=done).count() == 2


@pytest.mark.django_db
class TestStats:
    def test_counts_popular_options_and_average_duration(self) -> None:
        questionnaire = QuestionnaireFactory(is_published=True)
        question = QuestionFactory(questionnaire=questionnaire)
        popular = AnswerOptionFactory(question=question)
        rare = AnswerOptionFactory(question=question)
        questionnaire.refresh_from_db()

        for option in (popular, popular, rare):
            respondent = UserFactory()
            SurveyResultService.submit(
                questionnaire=questionnaire,
                respondent_id=respondent.id,
                answers=[{"question": question.id, "options": [option.id]}],
            )

        stats = SurveyResultService.stats(questionnaire=questionnaire)

        assert stats["responses"] == 3
        assert stats["completed"] == 3
        assert stats["average_duration_seconds"] is not None
        tally = stats["questions"][0]
        assert tally["question"] == question.id
        assert tally["options"][0] == {
            "option": popular.id,
            "text": popular.text,
            "count": 2,
        }

    def test_stats_reflect_new_submissions_immediately(self) -> None:
        questionnaire = QuestionnaireFactory(is_published=True)
        question = QuestionFactory(questionnaire=questionnaire)
        option = AnswerOptionFactory(question=question)
        questionnaire.refresh_from_db()

        SurveyResultService.submit(
            questionnaire=questionnaire,
            respondent_id=UserFactory().id,
            answers=[{"question": question.id, "options": [option.id]}],
        )
        assert (
            SurveyResultService.stats(questionnaire=questionnaire)["responses"]
            == 1
        )

        SurveyResultService.submit(
            questionnaire=questionnaire,
            respondent_id=UserFactory().id,
            answers=[{"question": question.id, "options": [option.id]}],
        )

        assert (
            SurveyResultService.stats(questionnaire=questionnaire)["responses"]
            == 2
        )
