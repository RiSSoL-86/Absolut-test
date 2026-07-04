from http import HTTPStatus

import pytest

from apps.common.exceptions import CustomMessageException


class TestCustomMessageException:
    def test_defaults(self) -> None:
        exc = CustomMessageException()

        assert exc.custom_message is None
        assert exc.field is None
        assert exc.loc is None
        assert exc.status_code == HTTPStatus.BAD_REQUEST

    def test_falls_back_to_class_custom_message(self) -> None:
        class NotFoundError(CustomMessageException):
            custom_message = "gone"

        exc = NotFoundError()

        assert str(exc) == "gone"
        # The class-level default is left untouched.
        assert exc.custom_message == "gone"

    def test_explicit_message_overrides_class_message(self) -> None:
        class NotFoundError(CustomMessageException):
            custom_message = "gone"

        exc = NotFoundError("really gone")

        assert str(exc) == "really gone"
        assert exc.custom_message == "really gone"

    def test_subclass_can_override_status_code(self) -> None:
        class TeapotError(CustomMessageException):
            status_code = HTTPStatus.IM_A_TEAPOT

        assert TeapotError().status_code == HTTPStatus.IM_A_TEAPOT

    def test_is_raisable_as_an_exception(self) -> None:
        with pytest.raises(CustomMessageException, match="boom"):
            raise CustomMessageException("boom")
