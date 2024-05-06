from dataclasses import dataclass

import pytest

from misc_python_utils.dataclass_utils import FixedDict


@dataclass
class Base(FixedDict):
    base: int


@dataclass
class Foo(Base):
    foo: str


@dataclass
class Bar(Base):
    bar: str


@dataclass
class FooBar(Bar, Foo):
    pass


def test_fixed_dict():
    foo = FooBar(1, "foo", "bar")
    with pytest.raises(AttributeError):
        foo.dings = "dings"
