# flake8: noqa WPS202
from dataclasses import dataclass

import pytest
from beartype import beartype
from beartype.roar import BeartypeCallHintParamViolation
from nested_dataclass_serialization.dataclass_serialization_utils import (
    PythonBuiltinData,
)

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
    obj: Dataclass,  # noqa: ARG001
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
        wants_builtin(SomeClass())  # type: ignore  # noqa: PGH003
    wants_builtin((1, 2, "foo"))
    wants_builtin((1, 2, 3))
    wants_builtin({1, 2, 3})


@beartype
def wants_builtin(x: PythonBuiltinData):  # noqa: ANN201, ARG001
    pass


# just for learning about np.ndarray[(3,), np.dtype[np.floating]]
# def test_wants_1d_numpy_array() -> None:
#     with pytest.raises(BeartypeCallHintParamViolation):  # noqa: PT012
#         array = np.array([1, 2, 3])
#         wants_1d_np_array_len_3(array)
#     with pytest.raises(BeartypeCallHintParamViolation):  # noqa: PT012
#         array = np.array([[1, 2, 3]])
#         wants_1d_np_array_len_3(array)
#     wants_1d_np_array_len_3(np.array([1.0, 2.0, 3.0]))
#
#
# @beartype
# def wants_1d_np_array_len_3(x: np.ndarray[(3,), np.dtype[np.floating]]) -> Any:
#     """This function expects a 1D numpy array of length 3."""
#     return x
