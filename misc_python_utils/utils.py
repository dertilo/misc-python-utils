import itertools
import logging
import platform
import sys
import traceback
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from hashlib import sha1
from typing import Any, Generic, TypeVar

from slugify import slugify

_major, minor, _patch = platform.python_version().split(".")

logger = logging.getLogger(
    __name__,
)  # "The name is potentially a period-separated hierarchical", see: https://docs.python.org/3.10/library/logging.html


JsonLoadsOutput = (
    dict | list | str | int | float | bool | None
)  # forgot anything? set  cannot be handled by json
PythonBuiltinData = JsonLoadsOutput | tuple | set

T = TypeVar("T")
T_default = TypeVar("T_default")


class Singleton(type):
    """
    see: https://stackoverflow.com/questions/6760685/creating-a-singleton-in-python
    """

    _instances = {}  # noqa: RUF012

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


def sanitize_hexappend_filename(filename: str) -> str:
    """
    see: https://stackoverflow.com/questions/7406102/create-sane-safe-filename-from-any-unsafe-string
    """
    sane = "".join([c for c in filename if c.isalpha() or c.isdigit()]).rstrip()
    if sane != filename:
        hex_dings = sha1(filename.encode("utf-8")).hexdigest()  # noqa: S324
        sane = f"{sane}_{hex_dings}"
    return sane


_Element = TypeVar("_Element")
_GroupValue = TypeVar("_GroupValue")


def sorted_groupby(
    data: Iterable[_Element],
    get_groupby_val: Callable[[_Element], _GroupValue],
) -> dict[_GroupValue, list[_Element]]:
    return {
        k: list(g)
        for k, g in itertools.groupby(
            sorted(data, key=get_groupby_val),
            key=get_groupby_val,
        )
    }


_GroupKey = TypeVar("_GroupKey")
_CollapsedValue = TypeVar("_CollapsedValue")


@dataclass(slots=True, frozen=True)
class MergedGroup(Generic[_GroupKey, _CollapsedValue]):
    key: _GroupKey
    value: _CollapsedValue


def collapse_sequence(
    input_: Iterable,
    merge_fun: Callable[[list[_GroupValue]], _CollapsedValue],
    get_key_fun: Callable[[_Element], _GroupKey],
) -> list[MergedGroup]:
    return [
        MergedGroup(key, merge_fun(list(g)))
        for key, g in itertools.groupby(input_, key=get_key_fun)
    ]


def just_try(  # noqa: C901, PLR0913, WPS231
    supplier: Callable[[], T],
    default: T_default = None,
    reraise: bool = False,
    verbose: bool = False,
    print_stacktrace: bool = True,
    fail_return_message_builder: Callable[..., Any] | None = None,
    fail_print_message_supplier: Callable[..., Any] | None = None,
) -> T | T_default:
    try:
        out = supplier()
    except Exception as e:  # noqa: BLE001
        if verbose or reraise:
            m = (
                fail_print_message_supplier()
                if fail_print_message_supplier is not None
                else ""
            )
            logger.warning(f"\ntried and failed with: {e}\n{m}\n")
            if print_stacktrace:
                traceback.print_exc(file=sys.stderr)
        if reraise:
            raise
        if fail_return_message_builder is not None:
            out = fail_return_message_builder(error=e, sys_stderr=sys.stderr)
        else:
            out = default
    return out


def slugify_with_underscores(s: str) -> str:
    regex_pattern_to_allow_underscores = r"[^-a-z0-9_]+"
    return slugify(s, regex_pattern=regex_pattern_to_allow_underscores)


def slugify_en_olny(s: str) -> str:
    return slugify(s, regex_pattern=r"[^-a-z0-9]+")
