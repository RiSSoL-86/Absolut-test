from typing import TYPE_CHECKING

import pytest

from apps.users.tests.factories import UserFactory

if TYPE_CHECKING:
    from rest_framework.test import APIClient

    from apps.users.models import User

USERS_URL = "/api/users/"
DEFAULT_LIMIT = 20


@pytest.mark.django_db
class TestListUsers:
    def test_staff_lists_all_users_ordered_by_id(
        self, staff_client: APIClient, staff_user: User
    ) -> None:
        others = [UserFactory() for _ in range(3)]
        expected_ids = sorted(u.id for u in [staff_user, *others])

        response = staff_client.get(USERS_URL)

        assert response.status_code == 200
        body = response.json()
        assert body["count"] == len(expected_ids)
        assert [row["id"] for row in body["results"]] == expected_ids

    def test_row_has_expected_shape(
        self, staff_client: APIClient, staff_user: User
    ) -> None:
        other = UserFactory()

        response = staff_client.get(USERS_URL)

        assert {
            "id": other.id,
            "email": other.email,
            "first_name": other.first_name,
            "last_name": other.last_name,
            "role": other.get_role_display(),
            "is_active": other.is_active,
        } in response.json()["results"]

    def test_regular_user_is_forbidden(self, auth_client: APIClient) -> None:
        response = auth_client.get(USERS_URL)

        assert response.status_code == 403

    def test_anonymous_is_unauthorized(self, api_client: APIClient) -> None:
        response = api_client.get(USERS_URL)

        assert response.status_code == 401


@pytest.mark.django_db
class TestListUsersPagination:
    def test_response_is_a_paginated_envelope(
        self, staff_client: APIClient, staff_user: User
    ) -> None:
        response = staff_client.get(USERS_URL)

        assert response.status_code == 200
        assert set(response.json()) == {
            "count",
            "next",
            "previous",
            "results",
        }

    def test_first_page_is_capped_at_default_limit(
        self, staff_client: APIClient, staff_user: User
    ) -> None:
        # staff_user + enough others to overflow a single page.
        UserFactory.create_batch(DEFAULT_LIMIT)

        response = staff_client.get(USERS_URL)

        body = response.json()
        assert body["count"] == DEFAULT_LIMIT + 1
        assert len(body["results"]) == DEFAULT_LIMIT
        assert body["previous"] is None
        assert body["next"] is not None

    def test_offset_returns_the_remainder(
        self, staff_client: APIClient, staff_user: User
    ) -> None:
        UserFactory.create_batch(DEFAULT_LIMIT)

        response = staff_client.get(USERS_URL, {"offset": DEFAULT_LIMIT})

        body = response.json()
        assert response.status_code == 200
        assert len(body["results"]) == 1
        assert body["next"] is None
        assert body["previous"] is not None

    def test_pages_do_not_overlap_and_cover_everyone(
        self, staff_client: APIClient, staff_user: User
    ) -> None:
        UserFactory.create_batch(DEFAULT_LIMIT)

        first = staff_client.get(USERS_URL).json()["results"]
        second = staff_client.get(USERS_URL, {"offset": DEFAULT_LIMIT}).json()[
            "results"
        ]

        seen = [row["id"] for row in [*first, *second]]
        assert len(seen) == len(set(seen)) == DEFAULT_LIMIT + 1

    def test_offset_past_the_end_returns_empty(
        self, staff_client: APIClient, staff_user: User
    ) -> None:
        response = staff_client.get(USERS_URL, {"offset": 999})

        assert response.status_code == 200
        assert response.json()["results"] == []

    def test_client_can_control_the_page_size(
        self, staff_client: APIClient, staff_user: User
    ) -> None:
        UserFactory.create_batch(4)  # + staff_user -> 5 total

        body = staff_client.get(USERS_URL, {"limit": 2}).json()

        assert len(body["results"]) == 2
        assert body["count"] == 5
        assert body["next"] is not None
