import pytest
from django.db import IntegrityError, transaction

from apps.questions.tests.factories import (
    AnswerOptionFactory,
    QuestionFactory,
)


@pytest.mark.django_db
class TestQuestionStr:
    def test_joins_text_and_questionnaire(self) -> None:
        question = QuestionFactory(text="How are you?")

        expected = f"How are you? ({question.questionnaire})"
        assert str(question) == expected


@pytest.mark.django_db
class TestQuestionTextUniquePerQuestionnaire:
    def test_same_survey_rejects_case_insensitive_duplicate(self) -> None:
        question = QuestionFactory(text="Age?")

        with pytest.raises(IntegrityError), transaction.atomic():
            QuestionFactory(questionnaire=question.questionnaire, text="age?")

    def test_another_survey_may_reuse_the_text(self) -> None:
        QuestionFactory(text="Age?")
        QuestionFactory(text="Age?")


@pytest.mark.django_db
class TestAnswerOptionStr:
    def test_is_its_own_text(self) -> None:
        option = AnswerOptionFactory(text="Yes")

        assert str(option) == "Yes"


@pytest.mark.django_db
class TestAnswerOptionTextUniquePerQuestion:
    def test_same_question_rejects_case_insensitive_duplicate(self) -> None:
        option = AnswerOptionFactory(text="Yes")

        with pytest.raises(IntegrityError), transaction.atomic():
            AnswerOptionFactory(question=option.question, text="yes")
