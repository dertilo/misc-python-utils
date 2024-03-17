from dataclasses import dataclass

import pytest
from beartype import beartype
from beartype.roar import BeartypeCallHintParamViolation

from misc_python_utils.beartypes import Dataclass


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
