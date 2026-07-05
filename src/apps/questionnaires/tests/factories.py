import factory
from factory.django import DjangoModelFactory

from apps.questionnaires.models import Questionnaire
from apps.users.choices import Role
from apps.users.tests.factories import UserFactory


class QuestionnaireFactory(DjangoModelFactory):
    """A published survey owned by a fresh author-role user."""

    class Meta:
        model = Questionnaire

    title = factory.Sequence(lambda n: f"Questionnaire {n}")
    author = factory.SubFactory(UserFactory, role=Role.AUTHOR)
    is_published = True
