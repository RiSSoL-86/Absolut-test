from typing import TYPE_CHECKING, cast, final

from rest_framework_simplejwt.tokens import RefreshToken, Token

if TYPE_CHECKING:
    from django.contrib.auth.base_user import AbstractBaseUser
    from django.contrib.auth.models import AnonymousUser

    from apps.users.models import User


@final
class TokenService:
    """Issue and enrich JWT tokens for any delivery layer."""

    @staticmethod
    def apply_claims(token: Token, user: User) -> None:
        """Embed authorization claims (role, staff flag) into the token."""
        token["role"] = user.role
        token["is_staff"] = user.is_staff

    @staticmethod
    def get_for_user(user: User) -> dict[str, str]:
        """Return an access/refresh pair carrying the user's claims."""
        refresh = RefreshToken.for_user(user)
        TokenService.apply_claims(refresh, user)
        return {"access": str(refresh.access_token), "refresh": str(refresh)}

    @staticmethod
    def get_user_id(user: AbstractBaseUser | AnonymousUser) -> int:
        """Return the id of the authenticated ``request.user``."""
        return cast("User", user).pk
