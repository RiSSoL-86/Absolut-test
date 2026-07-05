from typing import TYPE_CHECKING, final

from apps.users.models import User

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from apps.users.choices import Role


@final
class UserService:
    """Application-level operations for the ``User`` model."""

    @staticmethod
    def create(
        email: str, first_name: str, last_name: str, password: str, role: Role
    ) -> User:
        """Register a new user with a hashed password."""
        return User.objects.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
            role=role,
        )

    @staticmethod
    def get_active(user_id: int) -> User | None:
        """Return the active user with this id, else None."""
        return User.objects.filter(pk=user_id, is_active=True).first()

    @staticmethod
    def get_all() -> QuerySet[User]:
        """Return all users, ordered by id."""
        return User.objects.order_by("id")
