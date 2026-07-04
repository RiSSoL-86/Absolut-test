import pytest
from django.db import IntegrityError, transaction

from apps.questionnaires.models import Questionnaire
from apps.questionnaires.tests.factories import QuestionnaireFactory


@pytest.mark.django_db
class TestQuestionnaireStr:
    def test_joins_title_and_author(self) -> None:
        questionnaire = QuestionnaireFactory(title="Survey")

        assert str(questionnaire) == f"Survey ({questionnaire.author})"


@pytest.mark.django_db
class TestQuestionnaireTitleUniquePerAuthor:
    def test_same_author_cannot_reuse_title_ignoring_case(self) -> None:
        questionnaire = QuestionnaireFactory(title="My Survey")

        with pytest.raises(IntegrityError), transaction.atomic():
            QuestionnaireFactory(
                author=questionnaire.author, title="my survey"
            )

    def test_different_authors_may_share_a_title(self) -> None:
        QuestionnaireFactory(title="Shared")
        QuestionnaireFactory(title="Shared")

        assert Questionnaire.objects.filter(title="Shared").count() == 2
