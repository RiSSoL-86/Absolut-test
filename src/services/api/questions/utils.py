from typing import TYPE_CHECKING

from rest_framework.exceptions import PermissionDenied

from services.jwt_extensions.services import TokenService

if TYPE_CHECKING:
    from rest_framework_simplejwt.tokens import Token

    from apps.questionnaires.models import Questionnaire


def assert_draft_owned(questionnaire: Questionnaire, token: Token) -> None:
    """Allow writes only to the owner or an admin, before publishing."""
    owns = questionnaire.author_id == TokenService.get_user_id(token=token)
    if not (TokenService.is_staff(token=token) or owns):
        raise PermissionDenied("You can only edit your own questionnaire.")
    if questionnaire.is_published:
        raise PermissionDenied("A published questionnaire cannot be changed.")
