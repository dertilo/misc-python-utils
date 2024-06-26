from collections.abc import Iterable, Iterator
from typing import TypeVar

from result import Result

T = TypeVar("T", covariant=True)  # Success type
E = TypeVar("E", covariant=True)  # Error type


def ok_only(results: Iterable[Result[T, E]]) -> Iterator[T]:
    yield from (r.unwrap() for r in results if r.is_ok())
