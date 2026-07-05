import uuid

from django.db import models

from apps.common.models import TimeStampedAbstractModel, UUIAbstractModel


class TestUUIAbstractModel:
    def test_is_abstract(self) -> None:
        assert UUIAbstractModel._meta.abstract

    def test_id_is_a_uuid7_primary_key(self) -> None:

        assert isinstance(field, models.UUIDField)
        assert field.primary_key
        assert field.default is uuid.uuid7
        assert field.editable is False


class TestTimeStampedAbstractModel:
    def test_is_abstract(self) -> None:
        assert TimeStampedAbstractModel._meta.abstract

    def test_created_timestamp_is_set_on_insert_only(self) -> None:
        field = TimeStampedAbstractModel._meta.get_field("created_timestamp")

        assert field.auto_now_add is True
        assert field.auto_now is False
        assert field.editable is False

    def test_updated_timestamp_is_refreshed_on_every_save(self) -> None:
        field = TimeStampedAbstractModel._meta.get_field("updated_timestamp")

        assert field.auto_now is True
        assert field.auto_now_add is False
        assert field.editable is False
