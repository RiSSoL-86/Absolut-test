import pytest

from apps.users.services import UserService
from apps.users.tests.factories import UserFactory


@pytest.mark.django_db
class TestGetActive:
    def test_returns_active_user_by_id(self) -> None:
        user = UserFactory()

        assert UserService.get_active(user.id) == user

    def test_returns_none_for_inactive_user(self) -> None:
        user = UserFactory(is_active=False)

        assert UserService.get_active(user.id) is None

    def test_returns_none_for_unknown_id(self) -> None:
        assert UserService.get_active(user_id=10_000) is None


@pytest.mark.django_db
class TestListAll:
    def test_returns_every_user(self) -> None:
        users = [UserFactory() for _ in range(3)]

        result = UserService.list_all()

        assert list(result) == sorted(users, key=lambda u: u.id)

    def test_includes_inactive_users(self) -> None:
        inactive = UserFactory(is_active=False)

        assert inactive in UserService.list_all()

    def test_is_ordered_by_id(self) -> None:
        UserFactory.create_batch(5)

        ids = [user.id for user in UserService.list_all()]

        assert ids == sorted(ids)

    def test_empty_when_no_users(self) -> None:
        assert list(UserService.list_all()) == []
