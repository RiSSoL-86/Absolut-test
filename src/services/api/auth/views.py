from typing import TYPE_CHECKING, Any, final, override

from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from apps.users.models import User
from services.api.auth.serializers import (
    RefreshSerializer,
    SignInSerializer,
    SignUpSerializer,
)
from services.jwt_extensions.services import TokenService

if TYPE_CHECKING:
    from rest_framework.request import Request


@final
class SignUpView(CreateAPIView[User]):
    """Register a user and return an access/refresh token pair."""

    serializer_class = SignUpSerializer
    permission_classes = (AllowAny,)

    @override
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            TokenService.get_for_user(user), status=status.HTTP_201_CREATED
        )


@final
class SignInView(TokenObtainPairView):
    """Authenticate by email + password and return an access/refresh pair."""

    serializer_class = SignInSerializer
    permission_classes = (AllowAny,)  # type: ignore[assignment]


@final
class RefreshView(TokenRefreshView):
    """Rotate the access/refresh pair, re-validating the user in the DB."""

    serializer_class = RefreshSerializer
    permission_classes = (AllowAny,)  # type: ignore[assignment]
