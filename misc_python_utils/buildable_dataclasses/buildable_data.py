import logging
from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Annotated, ClassVar, TypeVar

from beartype.vale import Is
from slugify import slugify

from misc_python_utils.beartypes import NeStr
from misc_python_utils.buildable_dataclasses.buildable import (
    Buildable,
    BuildableBehavior,
)
from misc_python_utils.file_utils.readwrite_files import read_jsonl, write_jsonl
from misc_python_utils.prefix_suffix import PrefixSuffix
from misc_python_utils.utils import slugify_en_olny, slugify_with_underscores

logger = logging.getLogger(
    __name__,
)  # "The name is potentially a period-separated hierarchical", see: https://docs.python.org/3.10/library/logging.html

SlugStr = Annotated[NeStr, Is[lambda s: slugify_with_underscores(s) == s]]
NameSlug = Annotated[NeStr, Is[lambda s: slugify_en_olny(s) == s]]


def is_cased_sluggy(s: NeStr) -> bool:
    regex_pattern_to_allow_underscores = r"[^-A-Za-z0-9_]+"
    return (
        slugify(s, regex_pattern=regex_pattern_to_allow_underscores, lowercase=False)
        == s
    )


CasedSlugStr = Annotated[NeStr, Is[lambda s: is_cased_sluggy(s)]]

TBuildableData = TypeVar("TBuildableData", bound="BuildableData")


@dataclass(slots=True)
class DataBuilder(BuildableBehavior[TBuildableData]):
    @classmethod
    def it_is_ready(cls, obj: TBuildableData) -> bool:
        return obj._is_data_valid  # noqa: SLF001

    @classmethod
    def build_it(cls, obj: TBuildableData) -> None:
        Path(obj.data_dir).mkdir(
            parents=True,
            exist_ok=True,
        )
        obj._build_data()  # noqa: SLF001
        obj._was_built = True  # noqa: SLF001 # tilo: this _was_built refers to "was built in this python-process"
        if not obj._is_data_valid:  # noqa: SLF001
            msg = f"{cls.__class__.__name__}: {obj.name} failed to build data in {obj.data_dir=}"
            raise AssertionError(msg)


@dataclass(kw_only=True)
class BuildableData(ABC, Buildable):
    """
    just some helper-methods / "convenience logic" like:
        - defining a "data_dir" that consists of a "base_dir" and a folder-name (the "name"-property here)
        - checking if data is valid (_is_data_valid) if so loading it (_load_data)
        - reminding you to implement a "_is_data_valid"- and "_build_data" method

    """

    base_dir: PrefixSuffix
    buildable_behavior: ClassVar[
        DataBuilder
    ] = DataBuilder()  # pyright: ignore [reportIncompatibleVariableOverride] ->TODO!
    __serialize_anyhow__: ClassVar[set[str]] = {"name"}

    @property
    def data_dir(self) -> str:
        return f"{self.base_dir}/{self.name}"

    @property
    def data_dir_prefix_suffix(self) -> PrefixSuffix:
        return PrefixSuffix(
            self.base_dir.prefix_key,
            f"{self.base_dir.suffix}/{self.name}",
        )

    @property
    @abstractmethod
    def name(self) -> NameSlug:
        ...

    @property
    @abstractmethod
    def _is_data_valid(self) -> bool:
        # if you want to rebuilt all the time check for "_was_built" here
        ...

    @abstractmethod
    def _build_data(self) -> None:
        """
        build/write data
        """
        ...


DataNode = BuildableData  # rebranding

SomeDataclass = TypeVar(
    "SomeDataclass",
)  # cannot use beartype here cause pycharm wont get it


@dataclass
class IterableDataClasses(ABC, Iterable[SomeDataclass]):
    @property
    def jsonl_file(self) -> str:
        return f"{self.data_dir}/data.jsonl.gz"

    @property
    @abstractmethod
    def element_type(self) -> type[SomeDataclass]:
        ...

    @property
    @abstractmethod
    def data_dir(self) -> str:
        ...

    def __iter__(self) -> Iterator[SomeDataclass]:
        clazz = self.element_type
        create_fun = (
            clazz.from_dict if hasattr(clazz, "from_dict") else lambda x: clazz(**x)
        )
        yield from (create_fun(d) for d in read_jsonl(self.jsonl_file))


@dataclass
class BuildableDataClasses(BuildableData, IterableDataClasses[SomeDataclass]):
    @property
    def _is_data_valid(self) -> bool:
        return Path(self.jsonl_file).is_file()

    @abstractmethod
    def _generate_dataclasses(self) -> Iterator[SomeDataclass]:
        raise NotImplementedError

    def _build_data(self) -> None:
        Path(self.data_dir).mkdir(parents=True, exist_ok=True)
        write_jsonl(
            self.jsonl_file,
            (
                dc.to_dict() if hasattr(dc, "to_dict") else asdict(dc)
                for dc in self._generate_dataclasses()
            ),
        )
        # write_file(f"{self.data_dir}/dag.html", mermaid_html_dag(self)) # TODO: cannot simply put this here cause almost always git repo is not clean which would throw exception here
