import factory
from factory.django import DjangoModelFactory

from apps.questionnaires.tests.factories import QuestionnaireFactory
from apps.questions.models import AnswerOption, Question


class QuestionFactory(DjangoModelFactory):
    """A single-answer question inside a fresh questionnaire."""

    class Meta:
        model = Question

    questionnaire = factory.SubFactory(QuestionnaireFactory)
    text = factory.Sequence(lambda n: f"Question {n}?")
    allow_multiple = False


class AnswerOptionFactory(DjangoModelFactory):
    """An option belonging to a fresh question."""

    class Meta:
        model = AnswerOption

    question = factory.SubFactory(QuestionFactory)
    text = factory.Sequence(lambda n: f"Option {n}")
