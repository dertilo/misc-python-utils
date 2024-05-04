from dataclasses import dataclass

import pytest

from misc_python_utils.data_validation_mro_mixin import (
    DataValidationMROMixin,
    MroDataValidationError,
)


# ----------- following classes are just for testing and show-casing -----------------
@dataclass
class NeStartEnd(DataValidationMROMixin):
    start: float
    end: float

    def _parse_validate_data(self) -> None:
        if self.end <= self.start:
            raise MroDataValidationError(f"{NeStartEnd.__class__.__name__} complains")


@dataclass
class NeStartEndMs(NeStartEnd):
    def _parse_validate_data(self) -> None:
        self.start = round(self.start * 1000)
        self.end = round(self.end * 1000)


@dataclass
class NiceText(DataValidationMROMixin):
    text: str

    def _parse_validate_data(self) -> None:
        if "bad" in self.text:
            raise MroDataValidationError(f"{NiceText.__class__.__name__} complains")


@dataclass(kw_only=True)
class NeStartEndMsNiceText(NeStartEndMs, NiceText):
    def _parse_validate_data(self) -> None:
        if "ugly" in self.text and self.start == 0.123:
            raise MroDataValidationError(
                f"{NeStartEndMsNiceText.__class__.__name__} complains",
            )


# -------------------------------------------------------------------------------------


def test_datavalidation_mro_mixin():
    NeStartEnd(1.0, 2.0)
    with pytest.raises(
        MroDataValidationError,
        match=f"{NeStartEnd.__class__.__name__} complains",
    ):
        NeStartEnd(2.0, 1.0)

    with pytest.raises(
        MroDataValidationError,
        match=f"{NeStartEnd.__class__.__name__} complains",
    ):
        NeStartEndMs(0.0, 0.000_1)

    with pytest.raises(
        MroDataValidationError,
        match=f"{NeStartEnd.__class__.__name__} complains",
    ):
        NeStartEndMsNiceText(start=0.0, end=0.000_1, text="good")

    with pytest.raises(
        MroDataValidationError,
        match=f"{NeStartEndMsNiceText.__class__.__name__} complains",
    ):
        NeStartEndMsNiceText(start=0.0, end=1.0, text="bad")

    with pytest.raises(
        MroDataValidationError,
        match=f"{NiceText.__class__.__name__} complains",
    ):
        NeStartEndMsNiceText(start=0.123, end=1.0, text="ugly")
