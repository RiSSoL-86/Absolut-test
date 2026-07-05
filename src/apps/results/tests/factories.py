import factory
from factory.django import DjangoModelFactory

from apps.questionnaires.tests.factories import QuestionnaireFactory
from apps.questions.tests.factories import (
    AnswerOptionFactory,
    QuestionFactory,
)
from apps.results.models import SurveyAnswer, SurveyResult
from apps.users.tests.factories import UserFactory


class SurveyResultFactory(DjangoModelFactory):
    """A respondent's result for a fresh questionnaire."""

    class Meta:
        model = SurveyResult

    questionnaire = factory.SubFactory(QuestionnaireFactory)
    respondent = factory.SubFactory(UserFactory)


class SurveyAnswerFactory(DjangoModelFactory):
    """A coherent answer: option -> question -> the result's questionnaire.

    Defaults build a valid graph; override ``result``/``question``/``option``
    together to exercise the validation rules.
    """

    class Meta:
        model = SurveyAnswer

    result = factory.SubFactory(SurveyResultFactory)
    question = factory.LazyAttribute(
        lambda o: QuestionFactory(questionnaire=o.result.questionnaire)
    )
    option = factory.LazyAttribute(
        lambda o: AnswerOptionFactory(question=o.question)
    )
