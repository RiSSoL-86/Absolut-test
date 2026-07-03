from typing import TYPE_CHECKING

import pytest

from apps.users.choices import Role

if TYPE_CHECKING:
    from rest_framework.test import APIClient

    from apps.users.models import User

ME_URL = "/api/users/me/"


@pytest.mark.django_db
class TestRetrieveMe:
    def test_returns_own_profile(
        self, auth_client: APIClient, user: User
    ) -> None:
        response = auth_client.get(ME_URL)

        assert response.status_code == 200
        assert response.json() == {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.get_role_display(),
            "is_active": user.is_active,
        }

    def test_requires_authentication(self, api_client: APIClient) -> None:
        response = api_client.get(ME_URL)

        assert response.status_code == 401

    def test_404_when_account_deactivated(
        self, auth_client: APIClient, user: User
    ) -> None:
        # The token stays valid (stateless auth), but the account is gone
        # from the "active users" set, so the profile resolves to 404.
        user.is_active = False
        user.save(update_fields=["is_active"])

        response = auth_client.get(ME_URL)

        assert response.status_code == 404


@pytest.mark.django_db
class TestUpdateMe:
    def test_patch_updates_editable_fields(
        self, auth_client: APIClient, user: User
    ) -> None:
        response = auth_client.patch(
            ME_URL,
            {"first_name": "New", "last_name": "Name", "role": Role.AUTHOR},
            format="json",
        )

        assert response.status_code == 200
        user.refresh_from_db()
        assert user.first_name == "New"
        assert user.last_name == "Name"
        assert user.role == Role.AUTHOR

    def test_read_only_fields_are_ignored(
        self, auth_client: APIClient, user: User
    ) -> None:
        original_email = user.email

        response = auth_client.patch(
            ME_URL,
            {"email": "hacker@evil.com", "is_active": False},
            format="json",
        )

        assert response.status_code == 200
        user.refresh_from_db()
        assert user.email == original_email
        assert user.is_active is True

    def test_put_replaces_writable_fields(
        self, auth_client: APIClient, user: User
    ) -> None:
        response = auth_client.put(
            ME_URL,
            {"first_name": "Full", "last_name": "Put", "role": Role.AUTHOR},
            format="json",
        )

        assert response.status_code == 200
        user.refresh_from_db()
        assert user.first_name == "Full"
        assert user.role == Role.AUTHOR

    def test_requires_authentication(self, api_client: APIClient) -> None:
        response = api_client.patch(ME_URL, {"first_name": "X"}, format="json")

        assert response.status_code == 401
