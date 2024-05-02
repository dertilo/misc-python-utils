import dataclasses
import logging
from dataclasses import dataclass
from typing import ClassVar, TypeVar

from typing_extensions import Self

from misc_python_utils.dataclass_utils import UNDEFINED, Undefined

TPrefixSuffix = TypeVar("TPrefixSuffix", bound="PrefixSuffix")
BASE_PATHES: dict[str, str | TPrefixSuffix] = {}
BASE_PATHES[
    "pwd"
] = "."  # noqa: S105 -> this is a false-positive! pwd does not stand for "password" but the "current path"
BASE_PATHES[
    "<are_assigned>"
] = "False"  # somehow hacky way to confirm that BASE_PATHES are assigned

logger = logging.getLogger(__name__)


@dataclass
class PrefixSuffix:
    prefix_key: str | Undefined = UNDEFINED
    suffix: str | Undefined = UNDEFINED

    prefix: str = dataclasses.field(init=False)
    __exclude_from_hash__: ClassVar[list[str]] = ["prefix"]

    def build(self) -> Self:
        logger.warning(f"don't call build on {self.__class__.__name__} -> DEPRECATED!")
        """
        more lazy than post_init, "builds" prefix, only needed in case one newer calls str()
        """
        return self

    def __repr__(self) -> str:
        """
        base_path may not exist no constraints here!
        """
        if BASE_PATHES["<are_assigned>"] != "False":
            self._set_prefix()
            repr_ = f"{self.prefix}/{self.suffix}"
        else:
            """
            inspect calls the __repr__ method before BASE_PATHES was initialized!!

            File "python3.9/inspect.py", line 2593, in __str__
            formatted = '{} = {}'.format(formatted, repr(self._default))
            File "misc-utils/misc_utils/prefix_suffix.py", line 35, in __repr__
            self.__set_prefix()
            File "misc-utils/misc_utils/prefix_suffix.py", line 22, in __set_prefix

            """
            this_is_only_used_for_hashing = f"{self.prefix_key}/{self.suffix}"
            repr_ = this_is_only_used_for_hashing
        return repr_

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
