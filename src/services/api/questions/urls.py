from django.urls import path

from services.api.questions.views import (
    OptionCreateView,
    OptionDetailView,
    QuestionCreateView,
    QuestionDetailView,
)

app_name = "questions"

urlpatterns = [
    path("", QuestionCreateView.as_view(), name="create"),
    path("<uuid:pk>/", QuestionDetailView.as_view(), name="detail"),
    path("options/", OptionCreateView.as_view(), name="option-create"),
    path(
        "options/<uuid:pk>/",
        OptionDetailView.as_view(),
        name="option-detail",
    ),
]
