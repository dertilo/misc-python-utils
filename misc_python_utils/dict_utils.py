from collections.abc import Iterator, Mapping, MutableMapping
from dataclasses import dataclass
from typing import Any

from misc_python_utils.utils import Singleton

# pyright: reportAny=false


@dataclass
class _NOT_EXISTING(metaclass=Singleton):  # noqa: N801
    pass


NOT_EXISTING = _NOT_EXISTING()

# if TYPE_CHECKING: # TODO: can pyright handle recursives types?
#     MappingOrAny = Mapping[str, "MappingOrAny"] | Any
# else:
MappingOrAny = Mapping[str, Any] | Any


def get_dict_paths(d: Mapping[str, MappingOrAny]) -> Iterator[list[str]]:
    for key, mapping_or_any in d.items():
        if isinstance(mapping_or_any, Mapping):
            for sub_k in get_dict_paths(
                mapping_or_any,
            ):
                yield [key, *sub_k]
        else:
            yield [key]


def get_val_from_nested_dict(
    d: Mapping[str, MappingOrAny],
    path: list[str],
) -> Any | _NOT_EXISTING:
    value: MappingOrAny | _NOT_EXISTING = NOT_EXISTING  # declaring MappingOrAny here kind of hints towards a recursive type
    for key in path:
        if key in d.keys():
            value = d[key]
            if isinstance(value, Mapping):
                d = value
        else:
            value = NOT_EXISTING
            break
    return value


def flatten_nested_dict(
    d: Mapping[str, MappingOrAny],
    key_path: list[str] | None = None,
    sep: str = "_",
) -> list[tuple[list[str], Any]]:
    items: list[tuple[list[str], Any]] = []  # tilo: pyright wants this declaration
    for k, v in d.items():
        new_key = [*key_path, k] if key_path is not None else [k]
        if isinstance(v, MutableMapping):
            items.extend(flatten_nested_dict(v, new_key, sep=sep))
        else:
            items.append((new_key, v))
    return items


def nest_flattened_dict(flattened: list[tuple[list[str], Any]]) -> dict[str, Any]:
    nested_dict: dict[str, Any] = {}  # pyright wants this declaration
    for path, value in flattened:
        set_val_in_nested_dict(nested_dict, path, value)
    return nested_dict


def set_val_in_nested_dict(d: dict[str, Any], path: list[str], value: Any) -> None:
    for i, key in enumerate(path):
        if key not in d.keys():
            d[key] = {}

        if i == len(path) - 1:
            d[key] = value
        else:
            d = d[key]
