from dataclasses import InitVar, dataclass

import pytest
from beartype import beartype
from beartype.roar import BeartypeCallHintParamViolation

from misc_python_utils.beartypes import NeStr, nobeartype
from misc_python_utils.coop_mixins.data_validation_coop_mixin import (
    CoopDataValidationError,
    DataValidationCoopMixinBase,
    DataValidationCoopMixinBaseWithResult,
)
from misc_python_utils.error_handling.as_result_lambda import as_result_lambda


# ----------- following classes are just for testing and show-casing -----------------
@dataclass
class NeStartEnd(DataValidationCoopMixinBase):
    start: float
    end: float

    def _parse_validate_data(self) -> None:
        if self.end <= self.start:
            raise CoopDataValidationError(  # noqa: TRY003
                f"{NeStartEnd.__name__} complains"  # noqa: COM812, EM102
            )  # noqa: EM102, TRY003
        super()._parse_validate_data()


@dataclass
class NeStartEndMs(NeStartEnd):
    def _parse_validate_data(self) -> None:
        self.start = round(self.start * 1000)
        self.end = round(self.end * 1000)
        super()._parse_validate_data()


@dataclass
class NotTooLongNeStartEndMs(NeStartEndMs):
    some_limit: float = 7.0

    def _parse_validate_data(self) -> None:
        super()._parse_validate_data()
        if self.end - self.start > self.some_limit:
            raise CoopDataValidationError(  # noqa: TRY003
                f"{NotTooLongNeStartEndMs.__name__} complains",  # noqa: EM102
            )


@dataclass
class UnCooperativeDatum(NeStartEndMs, DataValidationCoopMixinBase):
    def _parse_validate_data(self) -> None:
        pass


@dataclass
class NiceText(DataValidationCoopMixinBase):
    text: str

    def _parse_validate_data(self) -> None:
        if "bad" in self.text:
            raise CoopDataValidationError(  # noqa: TRY003
                f"{NiceText.__name__} complains"  # noqa: COM812, EM102
            )
        super()._parse_validate_data()


@dataclass(kw_only=True)
class NeStartEndMsNiceText(NeStartEndMs, NiceText):
    def _parse_validate_data(self) -> None:
        if "ugly" in self.text and self.start == 0.123:  # noqa: PLR2004
            raise CoopDataValidationError(  # noqa: TRY003
                f"{NeStartEndMsNiceText.__name__} complains",  # noqa: EM102
            )
        super()._parse_validate_data()


# -------------------------------------------------------------------------------------


def test_datavalidation_coop_mixin():  # noqa: ANN201
    NeStartEnd(1.0, 2.0)
    with pytest.raises(AssertionError):
        UnCooperativeDatum(
            1.0,
            2.0,
        )  # in more complex scenarios there might still be some un-cooperative classes that one cannot detect
    with pytest.raises(
        CoopDataValidationError,
        match=f"{NeStartEnd.__name__} complains",
    ):
        NeStartEnd(2.0, 1.0)

    with pytest.raises(
        CoopDataValidationError,
        match=f"{NeStartEnd.__name__} complains",
    ):
        NeStartEndMs(0.0, 0.000_1)

    with pytest.raises(
        CoopDataValidationError,
        match=f"{NotTooLongNeStartEndMs.__name__} complains",
    ):
        NotTooLongNeStartEndMs(0.0, 1000.0)

    with pytest.raises(
        CoopDataValidationError,
        match=f"{NeStartEnd.__name__} complains",
    ):
        NeStartEndMsNiceText(start=0.0, end=0.000_1, text="good")

    with pytest.raises(
        CoopDataValidationError,
        match=f"{NiceText.__name__} complains",
    ):
        NeStartEndMsNiceText(start=0.0, end=1.0, text="bad")

    with pytest.raises(
        CoopDataValidationError,
        match=f"{NeStartEndMsNiceText.__name__} complains",
    ):
        NeStartEndMsNiceText(start=0.123, end=1.0, text="ugly")


# ----------- following classes are just for testing and show-casing -----------------
@dataclass
class NeStartEndAsResult(NeStartEnd, DataValidationCoopMixinBaseWithResult[NeStartEnd]):
    whatever: InitVar[str]

    def __post_init__(self, whatever: str):
        print(f"{whatever=}")  # noqa: T201
        super().__post_init__()


# -------------------------------------------------------------------------------------


def test_datavalidation_coop_mixin_with_result() -> None:
    o = NeStartEndAsResult(start=1.0, end=2.0, whatever="whatever")
    r = o.parse_validate_as_result()
    assert r.is_ok()

    with pytest.raises(
        CoopDataValidationError,
        match=f"{NeStartEnd.__name__} complains",
    ):
        NeStartEnd(1.0, 0.0)

    o = NeStartEndAsResult(
        start=1.0,
        end=0.0,
        whatever="whatever",
    )  # does not raise an error
    r = o.parse_validate_as_result()  # but forces you to handle a result
    assert r.is_err()


# -------------------------------------------------------------------------------------


aR = as_result_lambda(CoopDataValidationError)  # noqa: N816


def test_as_result_lambda() -> None:
    """
    very generic try-except but pollutes code with lambdas
    """
    o = aR(lambda: NiceText("bad"))
    assert o.is_err()
    assert isinstance(o.err(), CoopDataValidationError)


@dataclass
class NiceTextUnvalidated(NiceText, DataValidationCoopMixinBaseWithResult[NiceText]):
    pass


def test_as_result() -> None:
    o = NiceTextUnvalidated("nice")
    r = o.parse()
    assert r.is_ok()
    assert isinstance(r.ok(), NiceText)  # this is the funpart!

    bad = NiceTextUnvalidated("bad")
    r = bad.parse_validate_as_result()
    assert r.is_err()


@beartype  # normally these are added via import hooks (beartype claw)
@dataclass
class NiceTextWithBeartyped(NiceText):
    text: NeStr


@nobeartype
@dataclass
class NiceTextWithBeartypedUnvalidated(
    NiceTextWithBeartyped,
    DataValidationCoopMixinBaseWithResult[NiceTextWithBeartyped],
):
    pass


def test_validation_with_beartype_as_result() -> None:
    EMPTY_STR = ""
    o = NiceTextWithBeartypedUnvalidated(text=EMPTY_STR)
    r = o.parse()
    assert r.is_err()
    assert isinstance(r.err(), BeartypeCallHintParamViolation)
    o = NiceTextWithBeartypedUnvalidated("nice")
    r = o.parse()
    assert r.is_ok()
    assert isinstance(r.ok(), NiceText)  # this is the funpart!

    bad = NiceTextWithBeartypedUnvalidated("bad")
    r = bad.parse()
    assert r.is_err()
