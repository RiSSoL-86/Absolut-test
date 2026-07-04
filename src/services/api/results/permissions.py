from typing import TYPE_CHECKING, Any, final, override

from rest_framework.permissions import BasePermission

from services.jwt_extensions.services import TokenService

if TYPE_CHECKING:
    from rest_framework.request import Request
    from rest_framework.views import APIView


@final
class StatsPermission(BasePermission):
    """Only the survey's author or an admin may read its statistics."""

    @override
    def has_object_permission(
        self, request: Request, view: APIView, obj: Any
    ) -> bool:
        token = request.auth
        return TokenService.is_staff(token=token) or (
            obj.author_id == TokenService.get_user_id(token=token)
        )
