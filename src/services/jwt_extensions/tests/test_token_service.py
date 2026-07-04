import pytest
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from apps.users.choices import Role
from apps.users.tests.factories import StaffUserFactory, UserFactory
from services.jwt_extensions.services import TokenService

pytestmark = pytest.mark.django_db


class TestApplyClaims:
    """``apply_claims`` writes the user's role/staff flag into the token."""

    def test_embeds_role_and_staff_flag(self) -> None:
        token = RefreshToken()
        user = StaffUserFactory(role=Role.AUTHOR)

        TokenService.apply_claims(token=token, user=user)

        assert token["role"] == Role.AUTHOR
        assert token["is_staff"] is True

    @pytest.mark.parametrize(
        ("role", "is_staff"),
        [
            (Role.READER, False),
            (Role.AUTHOR, False),
            (Role.AUTHOR, True),
        ],
    )
    def test_reflects_user_attributes(
        self, role: Role, is_staff: bool
    ) -> None:
        token = RefreshToken()
        user = UserFactory(role=role, is_staff=is_staff)

        TokenService.apply_claims(token=token, user=user)

        assert token["role"] == role
        assert token["is_staff"] == is_staff


class TestGetForUser:
    """``get_for_user`` returns a claim-carrying access/refresh pair."""

    def test_returns_access_and_refresh_strings(self) -> None:
        pair = TokenService.get_for_user(user=UserFactory())

        assert set(pair) == {"access", "refresh"}
        assert isinstance(pair["access"], str)
        assert isinstance(pair["refresh"], str)

    def test_access_token_carries_user_and_claims(self) -> None:
        user = StaffUserFactory(role=Role.AUTHOR)

        access = AccessToken(TokenService.get_for_user(user=user)["access"])

        # simplejwt stores the user id claim as a string.
        assert access[api_settings.USER_ID_CLAIM] == str(user.pk)
        assert access["role"] == Role.AUTHOR
        assert access["is_staff"] is True

    def test_refresh_token_carries_claims(self) -> None:
        user = StaffUserFactory(role=Role.AUTHOR)

        refresh = RefreshToken(TokenService.get_for_user(user=user)["refresh"])

        assert refresh["role"] == Role.AUTHOR
        assert refresh["is_staff"] is True


class TestGetUserId:
    def test_returns_primary_key(self) -> None:
        user = UserFactory()
        access = AccessToken(TokenService.get_for_user(user=user)["access"])

        assert TokenService.get_user_id(token=access) == user.pk
