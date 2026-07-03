from typing import TYPE_CHECKING

import pytest
from rest_framework_simplejwt.tokens import AccessToken

from apps.users.choices import Role
from apps.users.tests.factories import (
    DEFAULT_PASSWORD,
    StaffUserFactory,
    UserFactory,
)

if TYPE_CHECKING:
    from rest_framework.test import APIClient

SIGNIN_URL = "/api/auth/signin/"


@pytest.mark.django_db
class TestSignIn:
    def test_valid_credentials_return_token_pair(
        self, api_client: APIClient
    ) -> None:
        user = UserFactory()

        response = api_client.post(
            SIGNIN_URL,
            {"email": user.email, "password": DEFAULT_PASSWORD},
            format="json",
        )

        assert response.status_code == 200
        assert set(response.json()) == {"access", "refresh"}

    def test_token_carries_role_and_staff_claims(
        self, api_client: APIClient
    ) -> None:
        user = StaffUserFactory(role=Role.AUTHOR)

        response = api_client.post(
            SIGNIN_URL,
            {"email": user.email, "password": DEFAULT_PASSWORD},
            format="json",
        )

        access = AccessToken(response.json()["access"])
        assert access["user_id"] == str(user.id)
        assert access["role"] == Role.AUTHOR
        assert access["is_staff"] is True

    def test_wrong_password_is_rejected(self, api_client: APIClient) -> None:
        user = UserFactory()

        response = api_client.post(
            SIGNIN_URL,
            {"email": user.email, "password": "wrong-password"},
            format="json",
        )

        assert response.status_code == 401

    def test_unknown_email_is_rejected(self, api_client: APIClient) -> None:
        response = api_client.post(
            SIGNIN_URL,
            {"email": "ghost@example.com", "password": DEFAULT_PASSWORD},
            format="json",
        )

        assert response.status_code == 401

    def test_inactive_user_is_rejected(self, api_client: APIClient) -> None:
        user = UserFactory(is_active=False)

        response = api_client.post(
            SIGNIN_URL,
            {"email": user.email, "password": DEFAULT_PASSWORD},
            format="json",
        )

        assert response.status_code == 401
