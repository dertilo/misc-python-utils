from dataclasses import dataclass

import pytest

from misc_python_utils.dataclass_utils import DataclassDict, FixedDict


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


def test_fixed_dict():  # noqa: ANN201
    foo = FooBar(1, "foo", "bar")
    with pytest.raises(AttributeError):
        foo.dings = "dings"


@dataclass
class SomeTestDataclassDict(DataclassDict):
    foo: str
    bar: int


def test_dataclass_dict() -> None:
    obj = SomeTestDataclassDict(foo="foo", bar=1)
    assert obj["foo"] == "foo"
    assert obj["bar"] == 1
    assert obj.to_dict() == {"foo": "foo", "bar": 1}
