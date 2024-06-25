from typing import Any, Generic, TypeVar

from misc_python_utils.rustedpy.result import Err, Ok, Result

T = TypeVar("T")  # Success type
E = TypeVar("E")  # Error type


class ResultFactory(Generic[T, E]):
    """
    just to fill missing types
    convinience class to create Ok and Err instances with proper generic types
    """

    @staticmethod
    def Result(ok_err: Ok[T, Any] | Err[E, Any]) -> Result[T, E]:
        match ok_err:
            case Ok(x):
                return Ok[T, E](x)
            case Err(x):
                return Err[E, T](x)

    @staticmethod
    def Ok(x: T) -> Ok[T, E]:
        return Ok[T, E](x)

    @staticmethod
    def Err(x: E) -> Err[E, T]:
        return Err[E, T](x)


# ErrA=Err[E,Any]
# OkA=Ok[T,Any]
