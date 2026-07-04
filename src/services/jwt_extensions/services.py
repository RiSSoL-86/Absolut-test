from typing import TYPE_CHECKING, final

from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken, Token

from apps.users.choices import Role

if TYPE_CHECKING:
    from apps.users.models import User


@final
class TokenService:
    """Issue JWT tokens and read the claims embedded in them."""

    @staticmethod
    def apply_claims(token: Token, user: User) -> None:
        """Embed authorization claims (role, staff flag) into the token."""
        token["role"] = user.role
        token["is_staff"] = user.is_staff

    @staticmethod
    def get_for_user(user: User) -> dict[str, str]:
        """Return an access/refresh pair carrying the user's claims."""
        refresh = RefreshToken.for_user(user)
        TokenService.apply_claims(token=refresh, user=user)
        return {"access": str(refresh.access_token), "refresh": str(refresh)}

    @staticmethod
    def _jwt_token(token: object) -> Token:
        if not isinstance(token, Token):
            raise TypeError("TokenService expects a SimpleJWT token.")
        return token

    @staticmethod
    def get_user_id(token: object) -> int:
        """Read the user id claim (SimpleJWT stores it as a string)."""
        jwt_token = TokenService._jwt_token(token=token)
        return int(jwt_token[api_settings.USER_ID_CLAIM])

    @staticmethod
    def get_role(token: object) -> Role:
        """Read the role claim embedded by ``apply_claims``."""
        jwt_token = TokenService._jwt_token(token=token)
        return Role(jwt_token["role"])

    @staticmethod
    def is_staff(token: object) -> bool:
        """Read the staff (admin) claim embedded by ``apply_claims``."""
        jwt_token = TokenService._jwt_token(token=token)
        return bool(jwt_token["is_staff"])
