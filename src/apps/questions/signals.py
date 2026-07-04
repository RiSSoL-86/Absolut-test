from typing import Any

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.questionnaires.models import Questionnaire
from apps.questions.models import AnswerOption, Question


@receiver(post_save, sender=Question)
def add_question_to_order(
    instance: Question, created: bool, **kwargs: Any
) -> None:
    """When a question is created, append its id to the survey's order."""
    if not created:
        return
    questionnaire = Questionnaire.objects.get(pk=instance.questionnaire_id)
    questionnaire.question_order.append(instance.pk)
    questionnaire.save(update_fields=["question_order"])


@receiver(post_delete, sender=Question)
def remove_question_from_order(instance: Question, **kwargs: Any) -> None:
    """When a question is deleted, drop its id from the survey's order."""
    questionnaire = Questionnaire.objects.filter(
        pk=instance.questionnaire_id
    ).first()
    if questionnaire is None:
        return
    if instance.pk in questionnaire.question_order:
        questionnaire.question_order.remove(instance.pk)
        questionnaire.save(update_fields=["question_order"])


@receiver(post_save, sender=AnswerOption)
def add_option_to_order(
    instance: AnswerOption, created: bool, **kwargs: Any
) -> None:
    """When an option is created, append its id to the question's order."""
    if not created:
        return
    question = Question.objects.get(pk=instance.question_id)
    question.option_order.append(instance.pk)
    question.save(update_fields=["option_order"])


@receiver(post_delete, sender=AnswerOption)
def remove_option_from_order(instance: AnswerOption, **kwargs: Any) -> None:
    """When an option is deleted, drop its id from the question's order."""
    question = Question.objects.filter(pk=instance.question_id).first()
    if question is None:
        return
    if instance.pk in question.option_order:
        question.option_order.remove(instance.pk)
        question.save(update_fields=["option_order"])
