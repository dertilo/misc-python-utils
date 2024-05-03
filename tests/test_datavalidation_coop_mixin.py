from dataclasses import dataclass

import pytest

from misc_python_utils.data_validation_coop_mixin import (
    CoopDataValidationError,
    DataValidationCoopMixinBase,
    DataValidationCoopMixinBaseWithResult,
)


# ----------- following classes are just for testing and show-casing -----------------
@dataclass
class NeStartEnd(DataValidationCoopMixinBase):
    start: float
    end: float

    def _parse_validate_data(self) -> None:
        if self.end <= self.start:
            raise CoopDataValidationError(f"{NeStartEnd.__class__.__name__} complains")
        super()._parse_validate_data()


@dataclass
class NeStartEndMs(NeStartEnd):
    def _parse_validate_data(self) -> None:
        self.start = round(self.start * 1000)
        self.end = round(self.end * 1000)
        super()._parse_validate_data()


@dataclass
class NiceText(DataValidationCoopMixinBase):
    text: str

    def _parse_validate_data(self) -> None:
        if "bad" in self.text:
            raise CoopDataValidationError(f"{NiceText.__class__.__name__} complains")
        super()._parse_validate_data()


@dataclass(kw_only=True)
class NeStartEndMsNiceText(NeStartEndMs, NiceText):
    def _parse_validate_data(self) -> None:
        if "ugly" in self.text and self.start == 0.123:
            raise CoopDataValidationError(
                f"{NeStartEndMsNiceText.__class__.__name__} complains"
            )
        super()._parse_validate_data()


# -------------------------------------------------------------------------------------


def test_datavalidation_coop_mixin():
    NeStartEnd(1.0, 2.0)
    with pytest.raises(
        CoopDataValidationError,
        match=f"{NeStartEnd.__class__.__name__} complains",
    ):
        NeStartEnd(2.0, 1.0)

    with pytest.raises(
        CoopDataValidationError,
        match=f"{NeStartEnd.__class__.__name__} complains",
    ):
        NeStartEndMs(0.0, 0.000_1)

    with pytest.raises(
        CoopDataValidationError,
        match=f"{NeStartEnd.__class__.__name__} complains",
    ):
        NeStartEndMsNiceText(start=0.0, end=0.000_1, text="good")

    with pytest.raises(
        CoopDataValidationError,
        match=f"{NeStartEndMsNiceText.__class__.__name__} complains",
    ):
        NeStartEndMsNiceText(start=0.0, end=1.0, text="bad")

    with pytest.raises(
        CoopDataValidationError,
        match=f"{NiceText.__class__.__name__} complains",
    ):
        NeStartEndMsNiceText(start=0.123, end=1.0, text="ugly")


# ----------- following classes are just for testing and show-casing -----------------
@dataclass
class NeStartEndAsResult(DataValidationCoopMixinBaseWithResult):
    start: float
    end: float

    def _parse_validate_data(self) -> None:
        if self.end <= self.start:
            raise CoopDataValidationError(f"{self.end=} <= {self.start=}")
        super()._parse_validate_data()


# -------------------------------------------------------------------------------------


def test_datavalidation_coop_mixin_with_result():
    o = NeStartEndAsResult(1.0, 0.0)
    r = o.parse_validate_as_result()
    assert r.is_err()
