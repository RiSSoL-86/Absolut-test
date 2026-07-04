from django.urls import path

from services.api.auth.views import RefreshView, SignInView, SignUpView

app_name = "auth"

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("signin/", SignInView.as_view(), name="signin"),
    path("refresh/", RefreshView.as_view(), name="refresh"),
]
