from dataclasses import dataclass

import pytest

from misc_python_utils.coop_mixins.tofrom_dict_coop_mixin import (
    FromDictCoopMixin,
    ToDictCoopMixin,
)


# ----------- following classes are just for testing and show-casing -----------------
@dataclass(slots=True)
class TimeStampedLetter:
    letter: str
    time: float


@dataclass
class TimeStampedLetters(FromDictCoopMixin, ToDictCoopMixin):
    time_stamped_letters: list[TimeStampedLetter]

    @classmethod
    def _from_dict(cls, jsn: dict) -> dict:
        parsed = {
            "time_stamped_letters": [
                TimeStampedLetter(l, t)
                for l, t in zip(jsn["text"], jsn["times"], strict=False)
            ],
        }
        return super()._from_dict(jsn | parsed)

    def _to_dict(self) -> dict:
        dct = {
            "text": [tsl.letter for tsl in self.time_stamped_letters],
            "times": [tsl.time for tsl in self.time_stamped_letters],
        }
        return super()._to_dict() | dct


@dataclass
class SomeFloat(FromDictCoopMixin, ToDictCoopMixin):
    value: float

    @classmethod
    def _from_dict(cls, jsn: dict) -> dict:
        d = super()._from_dict(
            jsn,
        )  # just to demonstrate that one could change the order
        return d | {"value": float(jsn["value_str"].replace("p", "."))}

    def _to_dict(self) -> dict:
        return super()._to_dict() | {"value_str": f"{self.value:.1f}".replace(".", "p")}


@dataclass
class TimeStampedLettersAndSomeFloat(TimeStampedLetters, SomeFloat):
    @classmethod
    def _from_dict(cls, jsn: dict) -> dict:
        dct = super()._from_dict(jsn)
        modified_value = {"value": round(dct["value"] * 2)}
        return dct | modified_value

    def _to_dict(self) -> dict:
        dct = super()._to_dict()
        modified_again = {"value_str": f"modified to: {round(self.value)}"}
        return dct | modified_again


@dataclass(slots=True)
class UnCooperativeClass(ToDictCoopMixin):
    def _to_dict(self) -> dict:
        return {"whatever": "foobar"}


# -------------------------------------------------------------------------------------


def test_from_to_dict_coop_mixin():
    jsn = {
        "text": ["a", "b", "c"],
        "times": [1.0, 2.0, 3.0],
        "value_str": "42p5",
    }
    obj = TimeStampedLetters.from_dict(jsn)
    assert obj.time_stamped_letters[0].letter == "a"

    obj = TimeStampedLettersAndSomeFloat.from_dict(jsn)
    assert obj.time_stamped_letters[0].letter == "a"
    assert obj.value == round(42.5 * 2)

    assert obj.to_dict() == jsn | {
        "value_str": "modified to: 85",
    }  # cause TimeStampedLettersAndSomeFloat modified the value

    obj = UnCooperativeClass()
    with pytest.raises(
        AssertionError,
        match=f" all subclasses of {obj.__class__.__name__} are UN-cooperative!",
    ):
        obj.to_dict()
