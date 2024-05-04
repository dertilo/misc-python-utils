from dataclasses import dataclass

from misc_python_utils.from_dict_mro_mixin import FromDictCoopMixin


# ----------- following classes are just for testing and show-casing -----------------
@dataclass(slots=True)
class TimeStampedLetter:
    letter: str
    time: float


@dataclass
class TimeStampedLetters(FromDictCoopMixin):
    time_stamped_letters: list[TimeStampedLetter]

    @classmethod
    def _from_dict(cls, jsn: dict) -> dict:
        parsed = {
            "time_stamped_letters": [
                TimeStampedLetter(l, t)
                for l, t in zip(jsn["text"], jsn["times"], strict=False)
            ]
        }
        return super()._from_dict(jsn | parsed)


@dataclass
class SomeFloat(FromDictCoopMixin):
    value: float

    @classmethod
    def _from_dict(cls, jsn: dict) -> dict:
        d = super()._from_dict(
            jsn
        )  # just to demonstrate that one could change the order
        return d | {"value": float(jsn["whatever"])}


@dataclass
class TimeStampedLettersAndSomeFloat(TimeStampedLetters, SomeFloat):
    pass


# -------------------------------------------------------------------------------------


def test_from_dict_coop_mixin():
    jsn = {
        "text": ["a", "b", "c"],
        "times": [1.0, 2.0, 3.0],
        "whatever": 42,
    }
    obj = TimeStampedLetters.from_dict(jsn)
    assert obj.time_stamped_letters[0].letter == "a"

    obj = TimeStampedLettersAndSomeFloat.from_dict(jsn)
    assert obj.time_stamped_letters[0].letter == "a"
    assert obj.value == 42.0
