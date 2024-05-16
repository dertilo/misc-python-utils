# flake8: noqa
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
E = TypeVar("E", covariant=True)  # Error type
U = TypeVar("U")
F = TypeVar("F")
P = ParamSpec("P")
R = TypeVar("R")
TBE = TypeVar(
    "TBE", bound=Exception
)  # tilo:  original code had "BaseException" here, but thats too liberal! one should not catch SystemExit, KeyboardInterrupt, etc.!


def as_result_logged(
    *exceptions: type[TBE],
    panic_exceptions: set[type[BaseException]] | None = None,
) -> Callable[[Callable[P, R]], Callable[P, Result[R, TBE]]]:
    """
    key-idea: results as_result is not working with beartype and not logging errors!
     -> instead of silently catching exceptions, we log them!
    based on: https://github.com/rustedpy/result/blob/021d9945f9cad12eb49386691d933c6688ac89a9/src/result/result.py#L439
    :exceptions: exceptions to catch and turn into ``Err(exc)``.
    :panic_exceptions: exceptions to catch and re-raise.
    Make a decorator to turn a function into one that returns a ``Result``.

    Regular return values are turned into ``Ok(return_value)``. Raised
    exceptions of the specified exception type(s) are turned into ``Err(exc)``.
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

    def decorator(f: Callable[P, R]) -> Callable[P, Result[R, TBE]]:
        """
        Decorator to turn a function into one that returns a ``Result``.
        """
        logger = logging.getLogger(f.__module__)

        @functools.wraps(f)
        @nobeartype
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Result[R, TBE]:
            try:
                o = beartype(f)(*args, **kwargs)
                return o if isinstance(o, OkErr) else Ok(o)
            except exceptions as exc:
                tb = traceback.format_exc()
                logger.error(tb)  # noqa: TRY400
                if type(exc) in panic_exceptions:
                    raise exc
                return Err(exc)

        return wrapper

    return decorator


def as_result_logged_panic_for_param_violations(
    *exceptions: type[TBE],
) -> Callable[[Callable[P, R]], Callable[P, Result[R, TBE]]]:
    """
    exceptions as result but panic for param violations
    """
    return as_result_logged(
        *exceptions, panic_exceptions={BeartypeCallHintParamViolation}
    )


# tb = traceback.format_tb(exc.__traceback__) # TODO: seems to be the same as tb = traceback.format_exc()
# ex = traceback.format_exception_only(type(exc), exc)
# logger.error("".join(tb+ex))
