import functools
from collections.abc import Callable
from typing import Generic, ParamSpec, TypeVar

from result import Err, Result

T_co = TypeVar("T_co", covariant=True)  # Success type
E = TypeVar("E")  # Error type
U = TypeVar("U")
F = TypeVar("F")
P = ParamSpec("P")
R = TypeVar("R")
TBE = TypeVar(
    "TBE",
    bound=Exception,
)  # tilo:  original code had "BaseException" here, but thats too liberal! one should not catch SystemExit, KeyboardInterrupt, etc.!


class EarlyReturnError(
    Exception,
    Generic[E],
):  # TODO: cannot make it generic like: Generic[E], python complains: TypeError: catching classes that do not inherit from BaseException is not allowed
    def __init__(self, error_value: E) -> None:
        self.error_value = error_value
        super().__init__(
            "if you see this, you forgot to add the 'return_earyl' decorator to the function inside which this exception was raised",
        )


def return_early(f: Callable[P, Result[R, E]]) -> Callable[P, Result[R, E]]:
    """
    based on: https://github.com/rustedpy/result/blob/021d9945f9cad12eb49386691d933c6688ac89a9/src/result/result.py#L439

    Decorator to turn a function into one that returns a ``Result``.
    -> this is extemely dangerous! cause when refactoring your code you easily produce exception-throwing over multiple layers of function-calls!
    """

    @functools.wraps(f)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Result[R, E]:
        try:
            return f(*args, **kwargs)
        except EarlyReturnError as exc:  # one cannot catch generic exceptions!
            exc: EarlyReturnError[E]  # but one can type-hint to keep pyright calm!
            return Err[E](
                exc.error_value,
            )  # E should be a type-union that includes all possible error-types

    return wrapper


def raise_early_return_error(e: E) -> EarlyReturnError[E]:
    raise EarlyReturnError(e)


return_err = raise_early_return_error


def unwrap_or_return(result: Result[T_co, E]) -> T_co:
    return result.unwrap_or_else(return_err)  # pyright: ignore [reportReturnType]


uR = unwrap_or_return  # noqa: N816
