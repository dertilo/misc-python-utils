from dataclasses import dataclass

import pytest

from misc_python_utils.coop_mixins.data_validation_mro_mixin import (
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
            raise MroDataValidationError(  # noqa: TRY003
                f"{NeStartEnd.__class__.__name__} complains"  # noqa: COM812, EM102
            )  # noqa: EM102, TRY003


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
            raise MroDataValidationError(  # noqa: TRY003
                f"{NiceText.__class__.__name__} complains"  # noqa: COM812, EM102
            )  # noqa: EM102, TRY003


@dataclass(kw_only=True)
class NeStartEndMsNiceText(NeStartEndMs, NiceText):
    def _parse_validate_data(self) -> None:
        if "ugly" in self.text and self.start == 0.123:  # noqa: PLR2004
            raise MroDataValidationError(  # noqa: TRY003
                f"{NeStartEndMsNiceText.__class__.__name__} complains",  # noqa: EM102
            )


# -------------------------------------------------------------------------------------


def test_datavalidation_mro_mixin():  # noqa: ANN201
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
