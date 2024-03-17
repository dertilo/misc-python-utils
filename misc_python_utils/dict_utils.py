from collections.abc import Iterator, MutableMapping
from dataclasses import dataclass
from typing import Any

from misc_python_utils.utils import Singleton


@dataclass
class _NOT_EXISTING(metaclass=Singleton):  # noqa: N801
    pass


NOT_EXISTING = _NOT_EXISTING()


def get_dict_paths(d: dict) -> Iterator[list[str]]:
    for k, sd in d.items():
        if isinstance(sd, dict):
            for sub_k in get_dict_paths(sd):
                yield [k, *sub_k]
        else:
            yield [k]


def get_val_from_nested_dict(d: dict, path: list[str]) -> Any | _NOT_EXISTING:
    for key in path:
        if key in d.keys():
            d = d[key]
        else:
            d = NOT_EXISTING
            break
    return d


def flatten_nested_dict(
    d: MutableMapping,
    key_path: list[str] | None = None,
    sep: str = "_",
) -> list[tuple[list[str], Any]]:
    items = []
    for k, v in d.items():
        new_key = [*key_path, k] if key_path is not None else [k]
        if isinstance(v, MutableMapping):
            items.extend(flatten_nested_dict(v, new_key, sep=sep))
        else:
            items.append((new_key, v))
    return items


def nest_flattened_dict(flattened: list[tuple[list[str], Any]]) -> dict:
    nested_dict = {}
    for path, value in flattened:
        set_val_in_nested_dict(nested_dict, path, value)
    return nested_dict


def set_val_in_nested_dict(d: dict, path: list[str], value: Any) -> None:
    for i, key in enumerate(path):
        if key not in d.keys():
            d[key] = {}

        if i == len(path) - 1:
            d[key] = value
        else:
            d = d[key]
