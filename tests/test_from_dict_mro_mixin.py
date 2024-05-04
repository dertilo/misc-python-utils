from collections.abc import Iterator
from dataclasses import dataclass

from misc_python_utils.from_dict_coop_mixin import FromDictMROMixin, KeyValue


# ----------- following classes are just for testing and show-casing -----------------
@dataclass(slots=True)
class TimeStampedLetter:
    letter: str
    time: float


@dataclass
class TimeStampedLetters(FromDictMROMixin):
    time_stamped_letters: list[TimeStampedLetter]

    @classmethod
    def _from_dict_self(cls, jsn: dict) -> Iterator[KeyValue]:
        yield "time_stamped_letters", [
            TimeStampedLetter(l, t)
            for l, t in zip(jsn["text"], jsn["times"], strict=False)
        ]


@dataclass
class SomeFloat(FromDictMROMixin):
    value: float

    @classmethod
    def _from_dict_self(cls, jsn: dict) -> Iterator[KeyValue]:
        yield "value", float(jsn["whatever"])


@dataclass
class TimeStampedLettersAndSomeFloat(TimeStampedLetters, SomeFloat):
    pass


# -------------------------------------------------------------------------------------


def test_from_dict_mro_mixin():
    jsn = {
        "text": ["a", "b", "c"],
        "times": [1.0, 2.0, 3.0],
        "whatever": 42,
    }
    obj = TimeStampedLetters.from_dict(jsn)
    assert obj.time_stamped_letters[0].letter == "a"

    obj = TimeStampedLettersAndSomeFloat.from_dict(jsn)
    assert obj.value == 42.0
