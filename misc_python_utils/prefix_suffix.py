import dataclasses
from dataclasses import dataclass
from typing import ClassVar, TypeVar

from typing_extensions import Self

TPrefixSuffix = TypeVar("TPrefixSuffix", bound="PrefixSuffix")
BASE_PATHES: dict[str, str | TPrefixSuffix] = {}
BASE_PATHES[
    "pwd"
] = "."  # noqa: S105 -> this is a false-positive! pwd does not stand for "password" but the "current path"


@dataclass
class PrefixSuffix:
    prefix_key: str
    suffix: str

    prefix: str = dataclasses.field(init=False)
    __exclude_from_hash__: ClassVar[list[str]] = ["prefix"]

    def __str__(self) -> str:
        self._set_prefix()
        return f"{self.prefix}/{self.suffix}"

    def from_str_same_prefix(self, path: str) -> Self:
        self._set_prefix()
        assert str(path).startswith(self.prefix)
        file_suffix = str(path).replace(f"{self.prefix}/", "")
        return PrefixSuffix(self.prefix_key, file_suffix)

    def _set_prefix(self) -> None:
        self.prefix = str(BASE_PATHES[self.prefix_key])
        # assert len(self.prefix) > 0, f"base_path is empty!"

    def __hash__(self):
        return hash(repr(self))
