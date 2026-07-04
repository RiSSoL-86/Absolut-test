from typing import TYPE_CHECKING

import pytest
from rest_framework.test import APIClient

from apps.users.choices import Role
from apps.users.tests.factories import StaffUserFactory, UserFactory
from services.jwt_extensions.services import TokenService

if TYPE_CHECKING:
    from apps.users.models import User


def authenticate(client: APIClient, user: User) -> APIClient:
    """Attach a valid ``Bearer`` access token for ``user`` to ``client``."""
    tokens = TokenService.get_for_user(user=user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
    return client


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def user(db) -> User:
    return UserFactory()


@pytest.fixture
def staff_user(db) -> User:
    return StaffUserFactory()


@pytest.fixture
def author_user(db) -> User:
    return UserFactory(role=Role.AUTHOR)


@pytest.fixture
def auth_client(api_client: APIClient, user: User) -> APIClient:
    """Client authenticated as the regular ``user`` fixture."""
    return authenticate(api_client, user)


@pytest.fixture
def staff_client(api_client: APIClient, staff_user: User) -> APIClient:
    """Client authenticated as the ``staff_user`` fixture."""
    return authenticate(api_client, staff_user)


@pytest.fixture
def author_client(api_client: APIClient, author_user: User) -> APIClient:
    """Client authenticated as the ``author_user`` fixture."""
    return authenticate(api_client, author_user)
