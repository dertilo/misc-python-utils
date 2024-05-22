from dataclasses import dataclass

import pytest
from beartype import beartype
from beartype.roar import BeartypeCallHintParamViolation

from misc_python_utils.beartypes import Dataclass, NeSequence, NeTuple
from misc_python_utils.utils import PythonBuiltinData


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
) -> None:
    return None


def test_wants_non_empty_tuple() -> None:
    with pytest.raises(BeartypeCallHintParamViolation):
        wants_non_empty_tuple(())
    wants_non_empty_tuple((1, 2, 3))
    # wants_non_empty_tuple((1,"foo",3)) # randomly might be caught be beartype


@beartype
def wants_non_empty_tuple(x: NeTuple[int]):  # noqa: ANN201, ARG001
    pass


def test_wants_non_empty_sequence() -> None:
    with pytest.raises(BeartypeCallHintParamViolation):
        wants_non_empty_sequence([])
    wants_non_empty_sequence([1, 2, 3])


@beartype
def wants_non_empty_sequence(x: NeSequence[int]):  # noqa: ANN201, ARG001
    pass


def test_wants_builtin() -> None:
    with pytest.raises(BeartypeCallHintParamViolation):
        wants_builtin(SomeClass())  # type: ignore
    wants_builtin((1, 2, "foo"))
    wants_builtin((1, 2, 3))
    wants_builtin({1, 2, 3})


@beartype
def wants_builtin(x: PythonBuiltinData):  # noqa: ANN201, ARG001
    pass
