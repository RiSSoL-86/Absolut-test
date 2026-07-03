from typing import TYPE_CHECKING, final

from apps.users.models import User

if TYPE_CHECKING:
    from django.db.models import QuerySet


@final
class UserService:
    """Application-level operations for the ``User`` model."""

    @staticmethod
    def get_active(user_id: int) -> User | None:
        """Return the active user with this id, else None."""
        return User.objects.filter(pk=user_id, is_active=True).first()

    @staticmethod
    def list_all() -> QuerySet[User]:
        """Return all users, ordered by id."""
        return User.objects.order_by("id")
