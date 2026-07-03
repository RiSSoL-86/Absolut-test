from typing import Any, final, override

from rest_framework import serializers

from apps.users.models import User


class UserBaseSerializer(serializers.ModelSerializer[User]):
    """Base serializer that renders ``role`` by its label, not its number."""

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "role",
            "is_active",
        )

    @override
    def to_representation(self, instance: User) -> dict[str, Any]:
        data = super().to_representation(instance)
        data["role"] = instance.get_role_display()
        return data


@final
class MeSerializer(UserBaseSerializer):
    """Current user's profile; name and role are editable by the owner."""

    class Meta(UserBaseSerializer.Meta):
        read_only_fields = ("id", "email", "is_active")


@final
class UserSerializer(UserBaseSerializer):
    """Read-only representation of a user returned by the API."""

    class Meta(UserBaseSerializer.Meta):
        read_only_fields = UserBaseSerializer.Meta.fields
