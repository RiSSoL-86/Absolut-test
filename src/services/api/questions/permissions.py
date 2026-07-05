from typing import TYPE_CHECKING, Any, final, override

from rest_framework.permissions import SAFE_METHODS, BasePermission

from apps.users.choices import Role
from services.jwt_extensions.services import TokenService

if TYPE_CHECKING:
    from rest_framework.request import Request
    from rest_framework.views import APIView


@final
class QuestionPermission(BasePermission):
    """Read for anyone authenticated; authors and admins write questions."""

    @override
    def has_permission(self, request: Request, view: APIView) -> bool:
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        return TokenService.get_role(
            token=request.auth
        ) == Role.AUTHOR or TokenService.is_staff(token=request.auth)

    @override
    def has_object_permission(
        self, request: Request, view: APIView, obj: Any
    ) -> bool:
        if request.method in SAFE_METHODS:
            return True
        if obj.questionnaire.is_published:
            self.message = "A published questionnaire cannot be changed."
            return False
        return TokenService.is_staff(token=request.auth) or (
            obj.questionnaire.author_id
            == TokenService.get_user_id(token=request.auth)
        )


@final
class OptionPermission(BasePermission):
    """Read for anyone authenticated; authors and admins write options."""

    @override
    def has_permission(self, request: Request, view: APIView) -> bool:
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        return TokenService.get_role(
            token=request.auth
        ) == Role.AUTHOR or TokenService.is_staff(token=request.auth)

    @override
    def has_object_permission(
        self, request: Request, view: APIView, obj: Any
    ) -> bool:
        if request.method in SAFE_METHODS:
            return True
        if obj.question.questionnaire.is_published:
            self.message = "A published questionnaire cannot be changed."
            return False
        return TokenService.is_staff(token=request.auth) or (
            obj.question.questionnaire.author_id
            == TokenService.get_user_id(token=request.auth)
        )
