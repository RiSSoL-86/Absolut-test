from django.urls import include, path

app_name = "api"

urlpatterns = [
    path("auth/", include("services.api.auth.urls")),
    path("users/", include("services.api.users.urls")),
    path(
        "questionnaires/",
        include("services.api.questionnaires.urls"),
    ),
    path(
        "questionnaires/<uuid:pk>/",
        include("services.api.results.urls"),
    ),
    path("questions/", include("services.api.questions.urls")),
]
