from typing import TYPE_CHECKING

import pytest
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import AccessToken

from apps.users.choices import Role
from apps.users.tests.factories import UserFactory
from services.api.auth.serializers import RefreshSerializer
from services.jwt_extensions.services import TokenService

if TYPE_CHECKING:
    from rest_framework.test import APIClient

REFRESH_URL = "/api/auth/refresh/"


@pytest.mark.django_db
class TestRefreshEndpoint:
    def test_returns_rotated_access_and_refresh(
        self, api_client: APIClient
    ) -> None:
        user = UserFactory(role=Role.AUTHOR)
        refresh = TokenService.get_for_user(user)["refresh"]

        response = api_client.post(
            REFRESH_URL, {"refresh": refresh}, format="json"
        )

        assert response.status_code == 200
        body = response.json()
        assert set(body) == {"access", "refresh"}
        access = AccessToken(body["access"])
        assert access["user_id"] == str(user.id)
        assert access["role"] == Role.AUTHOR

    def test_rotated_refresh_is_new_and_usable(
        self, api_client: APIClient
    ) -> None:
        user = UserFactory()
        refresh = TokenService.get_for_user(user)["refresh"]

        first = api_client.post(
            REFRESH_URL, {"refresh": refresh}, format="json"
        ).json()

        # A brand-new refresh token comes back, and it can itself be refreshed
        # again -- so an active client never falls back to SignIn.
        assert first["refresh"] != refresh
        again = api_client.post(
            REFRESH_URL, {"refresh": first["refresh"]}, format="json"
        )
        assert again.status_code == 200
        assert set(again.json()) == {"access", "refresh"}

    def test_rejects_refresh_for_deleted_user(
        self, api_client: APIClient
    ) -> None:
        user = UserFactory()
        refresh = TokenService.get_for_user(user)["refresh"]
        user.delete()

        response = api_client.post(
            REFRESH_URL, {"refresh": refresh}, format="json"
        )

        assert response.status_code == 401

    def test_rejects_refresh_for_inactive_user(
        self, api_client: APIClient
    ) -> None:
        user = UserFactory()
        refresh = TokenService.get_for_user(user)["refresh"]
        user.is_active = False
        user.save(update_fields=["is_active"])

        response = api_client.post(
            REFRESH_URL, {"refresh": refresh}, format="json"
        )

        assert response.status_code == 401

    def test_rejects_malformed_token(self, api_client: APIClient) -> None:
        response = api_client.post(
            REFRESH_URL, {"refresh": "not-a-token"}, format="json"
        )

        assert response.status_code == 401


@pytest.mark.django_db
class TestRefreshSerializer:
    """Serializer-level variation: drive ``validate`` directly."""

    def test_returns_rotated_pair_and_reapplies_claims(self) -> None:
        user = UserFactory(role=Role.AUTHOR)
        refresh = TokenService.get_for_user(user)["refresh"]

        serializer = RefreshSerializer(data={"refresh": refresh})
        assert serializer.is_valid(), serializer.errors

        data = serializer.validated_data
        assert set(data) == {"access", "refresh"}
        assert AccessToken(data["access"])["role"] == Role.AUTHOR
        assert data["refresh"] != refresh

    def test_raises_for_inactive_user(self) -> None:
        user = UserFactory()
        refresh = TokenService.get_for_user(user)["refresh"]
        user.is_active = False
        user.save(update_fields=["is_active"])

        serializer = RefreshSerializer(data={"refresh": refresh})

        with pytest.raises(AuthenticationFailed):
            serializer.is_valid(raise_exception=True)
