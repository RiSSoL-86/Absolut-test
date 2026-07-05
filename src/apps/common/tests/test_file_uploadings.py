import functools
import os
import uuid

from apps.common.services.file_uploadings import FileUploadService


def _assert_is_uuid(value: str) -> None:
    """Fail unless ``value`` is a valid UUID hex string."""
    uuid.UUID(value)


class TestUploadFileHandlerPath:
    def test_stores_file_under_the_base_path(self) -> None:
        result = FileUploadService.upload_file_handler_path(
            base_path="user/avatars", instance=None, filename="photo.png"
        )

        assert os.path.dirname(result) == "user/avatars"

    def test_keeps_the_original_extension(self) -> None:
        result = FileUploadService.upload_file_handler_path(
            base_path="base", instance=None, filename="photo.PNG"
        )

        assert result.endswith(".PNG")

    def test_replaces_the_original_name_with_a_uuid(self) -> None:
        result = FileUploadService.upload_file_handler_path(
            base_path="base", instance=None, filename="secret-report.png"
        )

        stem, _ = os.path.splitext(os.path.basename(result))
        _assert_is_uuid(stem)
        assert "secret-report" not in result

    def test_no_extension_when_the_source_has_none(self) -> None:
        result = FileUploadService.upload_file_handler_path(
            base_path="base", instance=None, filename="extensionless"
        )

        name = os.path.basename(result)
        assert "." not in name
        _assert_is_uuid(name)

    def test_generates_a_unique_name_on_every_call(self) -> None:
        first = FileUploadService.upload_file_handler_path(
            base_path="b", instance=None, filename="x.png"
        )
        second = FileUploadService.upload_file_handler_path(
            base_path="b", instance=None, filename="x.png"
        )
        
        assert first != second


class TestPrefixBasedUploadHandler:
    def test_returns_a_partial_bound_to_the_prefix(self) -> None:
        handler = FileUploadService.prefix_based_upload_handler(path="docs")

        assert isinstance(handler, functools.partial)

    def test_partial_builds_a_path_under_the_prefix(self) -> None:
        handler = FileUploadService.prefix_based_upload_handler(path="docs")

        # Django calls the handler as ``upload_to(instance, filename)``.
        result = handler(None, "manual.pdf")

        assert os.path.dirname(result) == "docs"
        assert result.endswith(".pdf")
