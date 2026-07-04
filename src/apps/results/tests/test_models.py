import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from apps.questions.tests.factories import (
    AnswerOptionFactory,
    QuestionFactory,
)
from apps.results.models import SurveyAnswer
from apps.results.tests.factories import (
    SurveyAnswerFactory,
    SurveyResultFactory,
)


@pytest.mark.django_db
class TestSurveyResultStr:
    def test_joins_questionnaire_and_respondent(self) -> None:
        result = SurveyResultFactory()

        expected = f"{result.questionnaire} - {result.respondent}"
        assert str(result) == expected


@pytest.mark.django_db
class TestSurveyResultUniquePerUser:
    def test_a_user_gets_one_result_per_questionnaire(self) -> None:
        result = SurveyResultFactory()

        with pytest.raises(IntegrityError), transaction.atomic():
            SurveyResultFactory(
                questionnaire=result.questionnaire,
                respondent=result.respondent,
            )


@pytest.mark.django_db
class TestSurveyAnswerConsistency:
    def test_option_must_belong_to_the_answered_question(self) -> None:
        result = SurveyResultFactory()
        question = QuestionFactory(questionnaire=result.questionnaire)
        foreign_option = AnswerOptionFactory()

        with pytest.raises(ValidationError, match="belong to the selected"):
            SurveyAnswerFactory(
                result=result, question=question, option=foreign_option
            )

    def test_question_must_belong_to_the_result_questionnaire(self) -> None:
        result = SurveyResultFactory()
        foreign_question = QuestionFactory()
        option = AnswerOptionFactory(question=foreign_question)

        with pytest.raises(ValidationError, match="result questionnaire"):
            SurveyAnswerFactory(
                result=result, question=foreign_question, option=option
            )


@pytest.mark.django_db
class TestAllowMultipleEnforcement:
    def test_single_answer_question_rejects_a_second_option(self) -> None:
        result = SurveyResultFactory()
        question = QuestionFactory(
            questionnaire=result.questionnaire, allow_multiple=False
        )
        first = AnswerOptionFactory(question=question)
        second = AnswerOptionFactory(question=question)
        SurveyAnswerFactory(result=result, question=question, option=first)

        with pytest.raises(ValidationError, match="multiple answers"):
            SurveyAnswerFactory(
                result=result, question=question, option=second
            )

    def test_multiple_answer_question_accepts_several_options(self) -> None:
        result = SurveyResultFactory()
        question = QuestionFactory(
            questionnaire=result.questionnaire, allow_multiple=True
        )
        first = AnswerOptionFactory(question=question)
        second = AnswerOptionFactory(question=question)

        SurveyAnswerFactory(result=result, question=question, option=first)
        SurveyAnswerFactory(result=result, question=question, option=second)

        assert question.answers.count() == 2

    def test_rule_holds_on_plain_save_not_only_admin_forms(self) -> None:
        result = SurveyResultFactory()
        question = QuestionFactory(
            questionnaire=result.questionnaire, allow_multiple=False
        )
        first = AnswerOptionFactory(question=question)
        second = AnswerOptionFactory(question=question)
        SurveyAnswer.objects.create(
            result=result, question=question, option=first
        )

        with pytest.raises(ValidationError):
            SurveyAnswer(
                result=result, question=question, option=second
            ).save()

    def test_the_same_option_cannot_be_answered_twice(self) -> None:
        result = SurveyResultFactory()
        question = QuestionFactory(
            questionnaire=result.questionnaire, allow_multiple=True
        )
        option = AnswerOptionFactory(question=question)
        SurveyAnswerFactory(result=result, question=question, option=option)

        with pytest.raises(ValidationError):
            SurveyAnswerFactory(
                result=result, question=question, option=option
            )
