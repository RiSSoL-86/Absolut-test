from typing import TYPE_CHECKING, Any

import pytest
from rest_framework_simplejwt.tokens import AccessToken

from apps.users.choices import Role
from apps.users.models import User

if TYPE_CHECKING:
    from rest_framework.test import APIClient

SIGNUP_URL = "/api/auth/signup/"


def payload(**overrides: Any) -> dict[str, Any]:
    data: dict[str, Any] = {
        "email": "new@example.com",
        "first_name": "New",
        "last_name": "User",
        "password": "strongpass123",
        "role": Role.READER,
    }
    data.update(overrides)
    return data


@pytest.mark.django_db
class TestSignUp:
    def test_creates_user_and_returns_token_pair(
        self, api_client: APIClient
    ) -> None:
        response = api_client.post(SIGNUP_URL, payload(), format="json")

        assert response.status_code == 201
        assert set(response.json()) == {"access", "refresh"}

        user = User.objects.get(email="new@example.com")
        assert user.first_name == "New"
        assert user.check_password("strongpass123")
        assert user.is_staff is False

    def test_password_is_stored_hashed(self, api_client: APIClient) -> None:
        api_client.post(SIGNUP_URL, payload(), format="json")

        user = User.objects.get(email="new@example.com")
        assert user.password != "strongpass123"

    def test_issued_token_carries_claims(self, api_client: APIClient) -> None:
        response = api_client.post(
            SIGNUP_URL, payload(role=Role.AUTHOR), format="json"
        )

        user = User.objects.get(email="new@example.com")
        access = AccessToken(response.json()["access"])
        assert access["user_id"] == str(user.id)
        assert access["role"] == Role.AUTHOR
        assert access["is_staff"] is False

    def test_duplicate_email_is_rejected(self, api_client: APIClient) -> None:
        api_client.post(SIGNUP_URL, payload(), format="json")

        response = api_client.post(SIGNUP_URL, payload(), format="json")

        assert response.status_code == 400
        assert "email" in response.json()

    def test_duplicate_email_is_case_insensitive(
        self, api_client: APIClient
    ) -> None:
        api_client.post(
            SIGNUP_URL, payload(email="Person@Example.com"), format="json"
        )

        response = api_client.post(
            SIGNUP_URL, payload(email="person@example.com"), format="json"
        )

        assert response.status_code == 400
        assert "email" in response.json()

    @pytest.mark.parametrize(
        ("field", "value"),
        [
            ("password", "short"),  # below the 8-char minimum
            ("email", "not-an-email"),
            ("role", 99),  # not a valid Role member
        ],
    )
    def test_invalid_input_returns_400(
        self, api_client: APIClient, field: str, value: Any
    ) -> None:
        response = api_client.post(
            SIGNUP_URL, payload(**{field: value}), format="json"
        )

        assert response.status_code == 400
        assert field in response.json()

    @pytest.mark.parametrize(
        "missing",
        ["email", "first_name", "last_name", "password", "role"],
    )
    def test_missing_required_field_returns_400(
        self, api_client: APIClient, missing: str
    ) -> None:
        data = payload()
        del data[missing]

        response = api_client.post(SIGNUP_URL, data, format="json")

        assert response.status_code == 400
        assert missing in response.json()
