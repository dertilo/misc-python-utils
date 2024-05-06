from dataclasses import dataclass

import pytest
from beartype import beartype
from beartype.roar import BeartypeCallHintParamViolation

from misc_python_utils.beartypes import Dataclass, NeSequence, NeTuple


@dataclass
class SomeDataclass:
    foo: str


class SomeClass:
    foo: str


def test_is_dataclass() -> None:
    with pytest.raises(BeartypeCallHintParamViolation):
        fun_want_dataclass(SomeClass())
    fun_want_dataclass(SomeDataclass("hello"))


@beartype
def fun_want_dataclass(
    obj: Dataclass,
) -> str:
    return obj.foo


def test_wants_non_empty_tuple() -> None:
    with pytest.raises(BeartypeCallHintParamViolation):
        wants_non_empty_tuple(())
    wants_non_empty_tuple((1, 2, 3))
    # wants_non_empty_tuple((1,"foo",3)) # randomly might be caught be beartype


@beartype
def wants_non_empty_tuple(x: NeTuple[int, ...]):
    pass


def test_wants_non_empty_sequence() -> None:
    with pytest.raises(BeartypeCallHintParamViolation):
        wants_non_empty_sequence([])
    wants_non_empty_sequence([1, 2, 3])


@beartype
def wants_non_empty_sequence(x: NeSequence[int]):
    pass
