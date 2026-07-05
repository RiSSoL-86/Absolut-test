from typing import TYPE_CHECKING, final, override

from rest_framework.exceptions import NotFound
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAdminUser

from apps.users.models import User
from apps.users.services import UserService
from services.api.users.serializers import MeSerializer, UserSerializer
from services.jwt_extensions.services import TokenService

if TYPE_CHECKING:
    from django.db.models import QuerySet


@final
class MeView(RetrieveUpdateAPIView[User]):
    """Return or update the authenticated user's own profile."""

    serializer_class = MeSerializer

    @override
    def get_object(self) -> User:
        token = self.request.auth
        user_id = TokenService.get_user_id(token=token)
        user = UserService.get_active(user_id=user_id)
        if user is None:
            raise NotFound("User no longer exists.")
        return user


@final
class UserListView(ListAPIView[User]):
    """List all users. Restricted to staff members."""

    serializer_class = UserSerializer
    permission_classes = (IsAdminUser,)

    @override
    def get_queryset(self) -> QuerySet[User]:
        return UserService.get_all()
