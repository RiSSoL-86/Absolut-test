from django.urls import path

from services.api.users.views import MeView, UserListView

app_name = "users"

urlpatterns = [
    path("", UserListView.as_view(), name="list"),
    path("me/", MeView.as_view(), name="me"),
]
