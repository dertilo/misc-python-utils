import dataclasses
from dataclasses import dataclass
from typing import ClassVar, TypeVar

from typing_extensions import Self

from misc_python_utils.dataclass_utils import UNDEFINED, Undefined

TPrefixSuffix = TypeVar("TPrefixSuffix", bound="PrefixSuffix")
BASE_PATHES: dict[str, str | TPrefixSuffix] = {}
BASE_PATHES[
    "pwd"
] = "."  # noqa: S105 -> this is a false-positive! pwd does not stand for "password" but the "current path"


@dataclass
class PrefixSuffix:
    prefix_key: str | Undefined = UNDEFINED
    suffix: str | Undefined = UNDEFINED

    prefix: str = dataclasses.field(init=False, default=UNDEFINED)
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
        self.prefix = BASE_PATHES[self.prefix_key]
        # assert len(self.prefix) > 0, f"base_path is empty!"

    def __hash__(self):
        return hash(repr(self))
