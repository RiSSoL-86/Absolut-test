from django.urls import path

from services.api.questionnaires.views import (
    QuestionnaireDetailView,
    QuestionnaireListCreateView,
    QuestionnairePublishView,
)

app_name = "questionnaires"

urlpatterns = [
    path("", QuestionnaireListCreateView.as_view(), name="list"),
    path("<uuid:pk>/", QuestionnaireDetailView.as_view(), name="detail"),
    path(
        "<uuid:pk>/publish/",
        QuestionnairePublishView.as_view(),
        name="publish",
    ),
]
