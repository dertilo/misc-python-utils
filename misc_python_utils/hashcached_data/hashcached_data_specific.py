from abc import abstractmethod
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from typing import ClassVar, TypeVar

from nested_dataclass_serialization.dataclass_serialization import (
    deserialize_dataclass,
    encode_dataclass,
)

from misc_python_utils.file_utils.readwrite_csv_files import write_dicts_to_csv
from misc_python_utils.file_utils.readwrite_files import (
    read_jsonl,
    read_lines,
    write_jsonl,
)
from misc_python_utils.hashcached_data.hashcached_data import HashCachedData

T = TypeVar("T")


@dataclass
class CachedDicts(HashCachedData, Iterable[T]):
    """
    coupling with source-code less strong -> use it for "longer" living data
    """

    jsonl_file_name: ClassVar[str] = "data.jsonl.gz"

    @property
    def jsonl_file(self) -> str:
        return f"{self.cache_dir}/{self.jsonl_file_name}"

    def _build_cache(self) -> None:
        write_jsonl(
            self.jsonl_file,
            self._generate_dicts_to_cache(),
        )

    @abstractmethod
    def _generate_dicts_to_cache(self) -> Iterator[dict]:
        raise NotImplementedError

    def __iter__(self) -> Iterator[dict]:
        yield from read_jsonl(self.jsonl_file)


@dataclass
class CachedCsv(HashCachedData, Iterable[T]):
    """
    coupling with source-code less strong -> use it for "longer" living data
    """

    data_file_name: ClassVar[str] = "data.csv.gz"

    @property
    def data_file(self) -> str:
        return f"{self.cache_dir}/{self.data_file_name}"

    def _build_cache(self) -> None:
        write_dicts_to_csv(
            self.data_file,
            self._generate_rows_to_cache(),
        )

    @abstractmethod
    def _generate_rows_to_cache(self) -> Iterator[dict]:
        raise NotImplementedError


@dataclass
class CachedDataclasses(CachedDicts, Iterable[T]):
    """
    this has a strong coupling with source-code -> use it for short-lived / very volatile cache!
    """

    @abstractmethod
    def generate_dataclasses_to_cache(self) -> Iterator[T]:
        raise NotImplementedError

    def _generate_dicts_to_cache(self) -> Iterator[dict]:
        counter = [-1]
        yield from (
            encode_dataclass(o)
            for counter[0], o in enumerate(self.generate_dataclasses_to_cache())
        )
        assert counter[0] > -1, f"{self.name} did not write anything!"

    def __iter__(self) -> Iterator[T]:
        yield from (deserialize_dataclass(s) for s in read_lines(self.jsonl_file))
