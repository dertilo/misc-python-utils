from collections.abc import Iterable, Iterator
from typing import TypeVar

from result import Result

T_co = TypeVar("T_co", covariant=True)  # Success type
E_co = TypeVar("E_co", covariant=True)  # Error type


def ok_only(results: Iterable[Result[T_co, E_co]]) -> Iterator[T_co]:
    yield from (r.unwrap() for r in results if r.is_ok())
