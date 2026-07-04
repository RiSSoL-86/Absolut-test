from typing import TYPE_CHECKING, Any, final

from django.db import transaction
from django.db.models import Avg, Count, F, Q
from django.utils import timezone

from apps.questions.models import AnswerOption, Question
from apps.results.models import SurveyAnswer, SurveyResult

if TYPE_CHECKING:
    from collections.abc import Sequence
    from uuid import UUID

    from apps.questionnaires.models import Questionnaire


@final
class SurveyResultService:
    """Taking a survey: progress, answers and per-survey statistics."""

    @staticmethod
    def answered_question_ids(
        questionnaire_id: UUID, respondent_id: int
    ) -> set[UUID]:
        """Ids of questions this respondent has already answered."""
        return set(
            SurveyAnswer.objects.filter(
                result__questionnaire_id=questionnaire_id,
                result__respondent_id=respondent_id,
            ).values_list("question_id", flat=True)
        )

    @staticmethod
    def next_question(
        questionnaire: Questionnaire, respondent_id: int
    ) -> Question | None:
        """First question in author order the respondent hasn't answered."""
        answered = SurveyResultService.answered_question_ids(
            questionnaire_id=questionnaire.id, respondent_id=respondent_id
        )
        for question_id in questionnaire.question_order:
            if question_id in answered:
                continue
            question = (
                Question.objects.prefetch_related("options")
                .filter(pk=question_id)
                .first()
            )
            if question is not None:
                return question
        return None

    @staticmethod
    @transaction.atomic
    def submit(
        questionnaire: Questionnaire,
        respondent_id: int,
        answers: Sequence[dict[str, Any]],
    ) -> SurveyResult:
        """Store validated answers, creating and completing the result."""
        result, _ = SurveyResult.objects.get_or_create(
            questionnaire=questionnaire, respondent_id=respondent_id
        )
        SurveyAnswer.objects.bulk_create(
            SurveyAnswer(
                result=result,
                question_id=item["question"],
                option_id=option_id,
            )
            for item in answers
            for option_id in item["options"]
        )
        SurveyResultService._complete_if_finished(
            result=result, questionnaire=questionnaire
        )
        return result

    @staticmethod
    def _complete_if_finished(
        result: SurveyResult, questionnaire: Questionnaire
    ) -> None:
        if result.completed_timestamp is not None:
            return
        answered = SurveyResultService.answered_question_ids(
            questionnaire_id=questionnaire.id,
            respondent_id=result.respondent_id,
        )
        expected = set(questionnaire.question_order)
        if expected and expected <= answered:
            result.completed_timestamp = timezone.now()
            result.save(update_fields=["completed_timestamp"])

    @staticmethod
    def stats(questionnaire: Questionnaire) -> dict[str, Any]:
        """Response counts, popular options and average completion time."""
        question_ids = questionnaire.question_order

        totals = SurveyResult.objects.filter(
            questionnaire=questionnaire
        ).aggregate(
            responses=Count("id"),
            completed=Count("id", filter=Q(completed_timestamp__isnull=False)),
            average=Avg(
                F("completed_timestamp") - F("started_timestamp"),
                filter=Q(completed_timestamp__isnull=False),
            ),
        )

        option_text = dict(
            AnswerOption.objects.filter(
                question_id__in=question_ids
            ).values_list("id", "text")
        )
        tallies = (
            SurveyAnswer.objects.filter(question_id__in=question_ids)
            .values("question_id", "option_id")
            .annotate(count=Count("*"))
            .order_by("question_id", "-count")
        )
        by_question: dict[UUID, list[dict[str, Any]]] = {}
        for row in tallies:
            by_question.setdefault(row["question_id"], []).append(
                {
                    "option": row["option_id"],
                    "text": option_text.get(row["option_id"]),
                    "count": row["count"],
                }
            )

        average = totals["average"]
        return {
            "responses": totals["responses"],
            "completed": totals["completed"],
            "average_duration_seconds": (
                average.total_seconds() if average is not None else None
            ),
            "questions_total": len(question_ids),
            "questions": [
                {"question": qid, "options": by_question[qid]}
                for qid in question_ids
                if qid in by_question
            ],
        }
