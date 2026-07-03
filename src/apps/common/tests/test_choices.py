from apps.common.choices import Language


class TestLanguage:
    def test_values(self) -> None:
        assert Language.RUSSIAN.value == 0
        assert Language.ENGLISH.value == 1

    def test_labels(self) -> None:
        assert str(Language.RUSSIAN.label) == "russian"
        assert str(Language.ENGLISH.label) == "english"

    def test_choices_pairs(self) -> None:
        assert Language.choices == [(0, "russian"), (1, "english")]

    def test_has_exactly_two_members(self) -> None:
        assert list(Language.values) == [0, 1]
