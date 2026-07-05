from django.urls import path

from services.api.results.views import (
    AnswersView,
    NextQuestionView,
    StatsView,
)

app_name = "results"

urlpatterns = [
    path(
        "next-question/",
        NextQuestionView.as_view(),
        name="next-question",
    ),
    path("answers/", AnswersView.as_view(), name="answers"),
    path("stats/", StatsView.as_view(), name="stats"),
]
