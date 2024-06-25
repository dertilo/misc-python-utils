import functools
import inspect

from beartype.typing import Callable, ParamSpec, TypeVar
from result import Err, Ok, Result

from misc_python_utils.beartypes import nobeartype

T = TypeVar("T", covariant=True)  # Success type
E = TypeVar("E", covariant=True)  # Error type
U = TypeVar("U")
F = TypeVar("F")
P = ParamSpec("P")
R = TypeVar("R")
TBE = TypeVar(
    "TBE",
    bound=Exception,
)  # tilo:  original code had "BaseException" here, but thats too liberal! one should not catch SystemExit, KeyboardInterrupt, etc.!


def as_result_lambda(
    *exceptions: type[TBE],
    panic_exceptions: set[type[BaseException]] | None = None,
) -> Callable[[Callable[[], R]], Result[R, TBE]]:
    panic_exceptions = set() if panic_exceptions is None else panic_exceptions
    if not exceptions or not all(
        inspect.isclass(exception)
        and issubclass(
            exception,
            Exception,
        )  # tilo: Exception instead of BaseException!
        for exception in exceptions
    ):
        msg = "as_result() requires one or more exception types"
        raise TypeError(msg)

    def decorator(f: Callable[[], R]) -> Result[R, TBE]:
        """
        Decorator to turn a function into one that returns a ``Result``.
        """

        @functools.wraps(f)
        @nobeartype
        def wrapper() -> Result[R, TBE]:
            try:
                o = f()
                return Ok(o)
            except exceptions as exc:
                if type(exc) in panic_exceptions:
                    raise
                return Err(exc)

        return wrapper()

    return decorator
