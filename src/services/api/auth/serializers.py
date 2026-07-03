from typing import Any, cast, final, override

from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import (
    AuthUser,
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken, Token

from apps.users.choices import Role
from apps.users.models import User
from apps.users.services import UserService
from services.jwt_extensions.services import TokenService


@final
class SignUpSerializer(serializers.ModelSerializer[User]):
    """Validate registration input and create a new user."""

    password = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(choices=Role.choices)

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "password", "role")

    @staticmethod
    def validate_email(value: str) -> str:
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("User already exists.")
        return value

    @override
    def create(self, validated_data: dict[str, Any]) -> User:
        return User.objects.create_user(**validated_data)


@final
class SignInSerializer(TokenObtainPairSerializer):
    """Authenticate by email + password; embed role/staff claims."""

    @override
    @classmethod
    def get_token(cls, user: AuthUser) -> Token:
        token = super().get_token(user)
        TokenService.apply_claims(token, cast("User", user))
        return token


@final
class RefreshSerializer(TokenRefreshSerializer):
    """Refresh the token pair, re-validating the user against the DB."""

    @override
    def validate(self, attrs: dict[str, Any]) -> dict[str, str]:
        refresh = RefreshToken(attrs["refresh"])
        user = UserService.get_active(refresh[api_settings.USER_ID_CLAIM])
        if user is None:
            raise AuthenticationFailed("User is inactive or removed.")
        TokenService.apply_claims(refresh, user)

        data = {"access": str(refresh.access_token)}
        refresh.set_jti()
        refresh.set_exp()
        refresh.set_iat()
        data["refresh"] = str(refresh)
        return data
