from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from typing import ClassVar, TypeVar

from misc_python_utils.buildable_dataclasses.buildable import (
    Buildable,
    BuildableBehavior,
)

TBuildableContainer = TypeVar("TBuildableContainer", bound="BuildableContainer")


Container = list | tuple | dict | set


class ContainerBuilder(BuildableBehavior[TBuildableContainer]):
    @classmethod
    def it_is_ready(cls, obj: TBuildableContainer) -> bool:
        return obj._was_built  # noqa: SLF001

    @classmethod
    def build_it(cls, obj: TBuildableContainer) -> None:
        for ele in obj:
            if hasattr(ele, "build"):
                ele.build()  # TODO: no shapeshifting here!!


TElement = TypeVar("TElement")


@dataclass
class BuildableContainer(Buildable, Iterable[TElement]):
    data: Container
    buildable_behavior: ClassVar[ContainerBuilder] = ContainerBuilder()

    def __iter__(self) -> Iterator[TElement]:
        # print(f"triggered build for {self.__class__.__name__}")
        if isinstance(self.data, list | tuple | set):
            yield from (x for x in self.data)
        elif isinstance(self.data, dict):
            yield from (v for v in self.data.values())
        else:
            raise NotImplementedError
