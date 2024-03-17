# flake8: noqa
from __future__ import annotations

import functools
import inspect
import logging
import traceback

from beartype import beartype
from beartype.roar import BeartypeCallHintParamViolation
from beartype.typing import Callable, ParamSpec, TypeVar
from result import Err, Ok, OkErr, Result

from misc_python_utils.beartypes import nobeartype

T = TypeVar("T", covariant=True)  # Success type
E = TypeVar("E")  # Error type
U = TypeVar("U")
F = TypeVar("F")
P = ParamSpec("P")
R = TypeVar("R")
TBE = TypeVar(
    "TBE", bound=Exception
)  # tilo:  original code had "BaseException" here, but thats too liberal! one should not catch SystemExit, KeyboardInterrupt, etc.!


def exceptions_as_err_logged(
    *exceptions: type[TBE],
    panic_exceptions: set[type[BaseException]] | None = None,
) -> Callable[[Callable[P, Result[R, E]]], Callable[P, Result[R, TBE | E]]]:
    """
    based on: https://github.com/rustedpy/result/blob/021d9945f9cad12eb49386691d933c6688ac89a9/src/result/result.py#L439
    :exceptions: exceptions to catch and turn into ``Err(exc)``.
    :panic_exceptions: exceptions to catch and re-raise.
    """
    panic_exceptions = set() if panic_exceptions is None else panic_exceptions
    if not exceptions or not all(
        inspect.isclass(exception)
        and issubclass(
            exception, Exception
        )  # tilo: Exception instead of BaseException!
        for exception in exceptions
    ):
        raise TypeError("as_result() requires one or more exception types")

    def decorator(f: Callable[P, Result[R, E]]) -> Callable[P, Result[R, TBE | E]]:
        """
        Decorator to turn a function into one that returns a ``Result``.
        """
        logger = logging.getLogger(
            f.__module__.replace("_", "."),
        )  # "The name is potentially a period-separated hierarchical", see: https://docs.python.org/3.10/library/logging.html

        @functools.wraps(f)
        @nobeartype
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Result[R, TBE | E]:
            try:
                return beartype(f)(*args, **kwargs)
            except exceptions as exc:
                tb = traceback.format_exc()
                logger.error(tb)  # noqa: TRY400
                if type(exc) in panic_exceptions:
                    raise exc
                return Err(exc)

        return wrapper

    return decorator


def exceptions_as_err_logged_panic_for_param_violation(
    *exceptions: type[TBE],
) -> Callable[[Callable[P, Result[R, E]]], Callable[P, Result[R, TBE | E]]]:
    """
    exceptions as result but panic for param violations
    """
    return exceptions_as_err_logged(
        *exceptions, panic_exceptions={BeartypeCallHintParamViolation}
    )


SomeError = TypeVar(
    "SomeError"
)  # tilo: one cannot really know all possible error-types, see "do" notation in result.py


class EarlyReturnError(Exception):
    def __init__(self, error_value: E) -> None:
        self.error_value = error_value
        super().__init__(
            "if you see this, you forgot to add the 'return_earyl' decorator to the function inside which this exception was raised"
        )


def return_early(f: Callable[P, Result[R, E]]) -> Callable[P, Result[R, E]]:
    """
    based on: https://github.com/rustedpy/result/blob/021d9945f9cad12eb49386691d933c6688ac89a9/src/result/result.py#L439

    Decorator to turn a function into one that returns a ``Result``.
    """

    @functools.wraps(f)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Result[R, E]:
        try:
            return f(*args, **kwargs)
        except EarlyReturnError as exc:
            return Err(exc.error_value)

    return wrapper


def raise_early_return_error(e: str) -> int:
    raise EarlyReturnError(e)


return_err = raise_early_return_error


def unwrap_or_return(obj: Result[T, E]) -> T:
    return obj.unwrap_or_else(return_err)


uR = unwrap_or_return
