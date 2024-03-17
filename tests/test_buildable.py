from dataclasses import dataclass, field

from misc_python_utils.buildable_dataclasses.buildable import Buildable
from misc_python_utils.buildable_dataclasses.buildable_container import (
    BuildableContainer,
)
from misc_python_utils.dataclass_utils import UNDEFINED, Undefined

EXPECTED_STATE = "hello"


@dataclass
class AnotherTestBuildable(Buildable):
    state: str | None = field(init=False, default=None)

    def _build_self(self) -> None:
        self.state = EXPECTED_STATE


@dataclass
class TestBuildable(Buildable):
    list_of_buildable: BuildableContainer | Undefined = UNDEFINED

    def _build_self(self) -> None:
        pass


def test_buildable() -> None:
    buildables = [AnotherTestBuildable(), AnotherTestBuildable()]
    buildable_container = BuildableContainer(buildables)
    TestBuildable(list_of_buildable=buildable_container).build()
    assert all(x.state == EXPECTED_STATE for x in buildables)
