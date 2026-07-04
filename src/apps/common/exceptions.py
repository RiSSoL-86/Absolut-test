from http import HTTPStatus
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.utils.functional import Promise


class CustomMessageException(Exception):
    """Base exception exposing a user-facing message and HTTP status."""

    custom_message: str | Promise | None = None
    field: str | None = None
    loc: list[str | int] | None = None
    status_code: HTTPStatus = HTTPStatus.BAD_REQUEST

    def __init__(self, message: str | None = None):
        super().__init__(message or self.custom_message)
        if message is not None:
            self.custom_message = message
