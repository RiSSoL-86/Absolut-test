import pytest

from apps.users.choices import Role
from apps.users.models import User
from apps.users.tests.factories import UserFactory
from services.api.auth.serializers import SignUpSerializer

VALID_DATA = {
    "email": "fresh@example.com",
    "first_name": "Fresh",
    "last_name": "Face",
    "password": "supersecret",
    "role": Role.AUTHOR,
}


@pytest.mark.django_db
class TestSignUpSerializer:
    def test_valid_data_creates_hashed_user(self) -> None:
        serializer = SignUpSerializer(data=VALID_DATA)
        assert serializer.is_valid(), serializer.errors

        user = serializer.save()

        assert isinstance(user, User)
        assert user.email == "fresh@example.com"
        assert user.role == Role.AUTHOR
        assert user.check_password("supersecret")
        assert user.password != "supersecret"

    def test_password_is_write_only(self) -> None:
        user = UserFactory()

        data = SignUpSerializer(instance=user).data

        assert "password" not in data

    def test_existing_email_fails_validation(self) -> None:
        UserFactory(email="taken@example.com")

        serializer = SignUpSerializer(
            data={**VALID_DATA, "email": "TAKEN@example.com"}
        )

        assert not serializer.is_valid()
        assert "email" in serializer.errors

    def test_short_password_fails_validation(self) -> None:
        serializer = SignUpSerializer(data={**VALID_DATA, "password": "short"})

        assert not serializer.is_valid()
        assert "password" in serializer.errors
