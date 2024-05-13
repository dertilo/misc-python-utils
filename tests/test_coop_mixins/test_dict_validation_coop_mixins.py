from dataclasses import dataclass

import pytest

from misc_python_utils.coop_mixins.data_validation_coop_mixin import (
    CoopDataValidationError,
    DataValidationCoopMixinBase,
)
from misc_python_utils.coop_mixins.tofrom_dict_coop_mixin import (
    FromDictCoopMixin,
    ToDictCoopMixin,
)

# ----------- following classes are just for testing and show-casing -----------------


@dataclass
class A(FromDictCoopMixin, ToDictCoopMixin, DataValidationCoopMixinBase):
    a: float

    def _parse_validate_data(self) -> None:
        if self.a < 0.0:
            raise CoopDataValidationError(  # noqa: TRY003
                f"{self.__class__.__name__} complains"  # noqa: COM812, EM102
            )  # noqa: EM102, TRY003
        super()._parse_validate_data()

    @classmethod
    def _from_dict(cls, jsn: dict) -> dict:
        return super()._from_dict(jsn) | {"a": float(jsn["a"].replace("a", "."))}

    def _to_dict(self) -> dict:
        return super()._to_dict() | {"a": f"{self.a:.1f}".replace(".", "a")}


@dataclass
class B(FromDictCoopMixin, ToDictCoopMixin, DataValidationCoopMixinBase):
    b: float

    def _parse_validate_data(self) -> None:
        if self.b < 0.0:
            raise CoopDataValidationError(  # noqa: TRY003
                f"{self.__class__.__name__} complains"  # noqa: COM812, EM102
            )  # noqa: EM102, TRY003
        super()._parse_validate_data()

    @classmethod
    def _from_dict(cls, jsn: dict) -> dict:
        return super()._from_dict(jsn) | {"b": float(jsn["b"].replace("b", "."))}

    def _to_dict(self) -> dict:
        return super()._to_dict() | {"b": f"{self.b:.1f}".replace(".", "b")}


@dataclass
class C(A, B, DataValidationCoopMixinBase):
    c: float

    def _parse_validate_data(self) -> None:
        if self.c < 0.0:
            raise CoopDataValidationError(  # noqa: TRY003
                f"{self.__class__.__name__} complains"  # noqa: COM812, EM102
            )  # noqa: EM102, TRY003
        super()._parse_validate_data()

    @classmethod
    def _from_dict(cls, jsn: dict) -> dict:
        return super()._from_dict(jsn) | {"c": float(jsn["c"].replace("c", "."))}

    def _to_dict(self) -> dict:
        return super()._to_dict() | {"c": f"{self.c:.1f}".replace(".", "c")}


# -------------------------------------------------------------------------------------


def test_from_to_dict_coop_mixin():  # noqa: ANN201
    jsn = {
        "a": "1a2",
        "b": "3b4",
        "c": "5c6",
    }
    obj = C.from_dict(jsn)
    assert obj.a == 1.2  # noqa: PLR2004
    assert obj.b == 3.4  # noqa: PLR2004
    assert obj.c == 5.6  # noqa: PLR2004

    assert obj.to_dict() == jsn


def test_from_to_dict_coop_mixin_data_violations():  # noqa: ANN201
    with pytest.raises(
        CoopDataValidationError,
        match=f"{A.__name__} complains",
    ):
        A.from_dict({"a": "-1a2"})

    with pytest.raises(
        CoopDataValidationError,
        match=f"{C.__name__} complains",  # because C is first in MRO!
    ):
        C.from_dict({"a": "-1a2", "b": "-3b4", "c": "-5c6"})


# -------------------------------------------------------------------------------------


@dataclass
class CparsingAB(A, B, DataValidationCoopMixinBase):
    c: float

    def _parse_validate_data(self) -> None:
        if self.a < 0.0:
            self.a = -self.a
        if self.b < 0.0:
            self.b = -self.b

        if self.c < 0.0:
            raise CoopDataValidationError(  # noqa: TRY003
                f"{self.__class__.__name__} complains"  # noqa: COM812, EM102
            )  # noqa: EM102, TRY003
        super()._parse_validate_data()

    @classmethod
    def _from_dict(cls, jsn: dict) -> dict:
        return super()._from_dict(jsn) | {"c": float(jsn["c"].replace("c", "."))}

    def _to_dict(self) -> dict:
        return super()._to_dict() | {"c": f"{self.c:.1f}".replace(".", "c")}


# -------------------------------------------------------------------------------------


def test_CparsingAB():  # noqa: ANN201
    obj = CparsingAB.from_dict({"a": "-1a2", "b": "-3b4", "c": "5c6"})
    assert (  # noqa: PT018
        obj.a == 1.2 and obj.b == 3.4 and obj.c == 5.6  # noqa: PLR2004
    )  # because CparsingAB parsed a and b
