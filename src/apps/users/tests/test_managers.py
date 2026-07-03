import pytest

from apps.users.choices import Role
from apps.users.models import User


@pytest.mark.django_db
class TestCreateUser:
    def test_creates_a_plain_active_user(self) -> None:
        user = User.objects.create_user(
            email="reader@example.com",
            password="s3cret",
            first_name="Read",
            last_name="Er",
        )

        assert user.is_staff is False
        assert user.is_superuser is False
        assert user.role == Role.READER
        assert user.check_password("s3cret")

    def test_email_is_normalized(self) -> None:
        user = User.objects.create_user(
            email="Reader@Example.COM",
            password="x",
            first_name="A",
            last_name="B",
        )

        # normalize_email lowercases only the domain part.
        assert user.email == "Reader@example.com"

    def test_password_is_hashed_not_stored_in_plain_text(self) -> None:
        user = User.objects.create_user(
            email="hash@example.com",
            password="plaintext",
            first_name="A",
            last_name="B",
        )

        assert user.password != "plaintext"

    def test_requires_an_email(self) -> None:
        with pytest.raises(ValueError, match="email address"):
            User.objects.create_user(
                email="",
                password="x",
                first_name="A",
                last_name="B",
            )


@pytest.mark.django_db
class TestCreateSuperuser:
    def test_creates_staff_superuser(self) -> None:
        admin = User.objects.create_superuser(
            email="admin@example.com",
            password="x",
            first_name="Ad",
            last_name="Min",
        )

        assert admin.is_staff is True
        assert admin.is_superuser is True

    def test_rejects_non_staff_superuser(self) -> None:
        with pytest.raises(ValueError, match="is_staff=True"):
            User.objects.create_superuser(
                email="admin@example.com",
                password="x",
                first_name="Ad",
                last_name="Min",
                is_staff=False,
            )

    def test_rejects_non_superuser_flag(self) -> None:
        with pytest.raises(ValueError, match="is_superuser=True"):
            User.objects.create_superuser(
                email="admin@example.com",
                password="x",
                first_name="Ad",
                last_name="Min",
                is_superuser=False,
            )


@pytest.mark.django_db
class TestGetByNaturalKey:
    def test_lookup_is_case_insensitive(self) -> None:
        user = User.objects.create_user(
            email="Case@Example.com",
            password="x",
            first_name="A",
            last_name="B",
        )

        assert User.objects.get_by_natural_key("case@example.com") == user
