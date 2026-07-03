from django.urls import include, path

app_name = "api"

urlpatterns = [
    path("auth/", include("services.api.auth.urls")),
    path("users/", include("services.api.users.urls")),
]
