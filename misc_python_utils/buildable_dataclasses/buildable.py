import dataclasses
import logging
from abc import ABC, abstractmethod
from collections import namedtuple
from dataclasses import dataclass, fields
from time import time
from typing import ClassVar, Generic, TypeVar, final

from typing_extensions import Self

from misc_python_utils.dataclass_utils import (
    MaybeEnforcedSlots,
    all_undefined_must_be_filled,
)

logger = logging.getLogger(
    __name__,
)  # "The name is potentially a period-separated hierarchical", see: https://docs.python.org/3.10/library/logging.html


class GotWasBuilt(ABC):
    @property
    @abstractmethod
    def _was_built(self) -> bool:
        ...


TBuildable = TypeVar("TBuildable", bound="Buildable")


class BuildableBehavior(ABC, Generic[TBuildable]):
    @classmethod
    @abstractmethod
    def it_is_ready(cls, obj: TBuildable) -> bool:
        ...

    @classmethod
    def build_it(cls, obj: TBuildable) -> None:
        pass


@dataclass
class DefaultBuildableBehavior(BuildableBehavior):
    def it_is_ready(self, obj: TBuildable) -> bool:
        return obj._was_built  # noqa: SLF001

    def build_it(self, obj: TBuildable) -> None:
        pass


NamedChild = namedtuple("NamedChild", "name child")  # noqa: PYI024


@dataclass(kw_only=True)
class Buildable(MaybeEnforcedSlots):
    """
    base-class for "buildable Dataclasses"

    key-idea: a Dataclass has fields (attributes) those can be interpreted as "dependencies"
        in order to "build" a Dataclass it is necessary to first build all ites dependencies (=children)

    the build-method essentially does 2 things:
        1. _build_all_children
        2. _build_self

    if the buildable-object "_is_ready" then it does NOT build any children and also not itself!
    """

    buildable_behavior: ClassVar[BuildableBehavior] = DefaultBuildableBehavior()

    _was_built: bool = dataclasses.field(default=False, init=False, repr=False)
    __serialize_anyhow__: ClassVar[set[str]] = {
        "name",
    }  # assuming that almost all have a name, but still not enforcing a name, serializing the name is needed for displaying it in mermaid dag

    @property
    def _is_ready(self) -> bool:
        return self.buildable_behavior.it_is_ready(self)

    @final  # does not enforce it but at least the IDE warns you!
    def build(
        self: Self,
    ) -> Self:
        """
        should NOT be overwritten!
        """
        if not self._is_ready:
            all_undefined_must_be_filled(self)
            self._build_all_children()
            start = time()
            self._build_self()
            self._was_built = True
            duration = time() - start
            min_dur_of_interest = 1.0
            if duration > min_dur_of_interest:
                logger.debug(
                    f"build_self of {self.__class__.__name__} took:{duration} seconds",
                )
                # traceback.print_stack()
        else:
            self._was_built = True  # being ready is as good as being built
        return self

    def _build_all_children(self) -> None:
        for nc in self.children:
            setattr(
                self,
                nc.name,
                nc.child.build(),
            )  # this potentially allows shape-shifting!

    @property
    def children(self) -> list[NamedChild]:
        objects = ((f.name, getattr(self, f.name)) for f in fields(self) if f.init)
        return [
            NamedChild(name, obj) for name, obj in objects if isinstance(obj, Buildable)
        ]

    def _build_self(self) -> None:
        self.buildable_behavior.build_it(self)
