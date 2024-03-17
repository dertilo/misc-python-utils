import pytest
from beartype.roar import (
    BeartypeCallHintParamViolation,
    BeartypeCallHintReturnViolation,
)
from result import Err, Ok, Result

from misc_python_utils.error_handling.as_result_logged import (
    as_result_logged_panic_for_param_violations,
)
from misc_python_utils.error_handling.exception_as_err import (
    EarlyReturnError,
    exceptions_as_err_logged,
    return_early,
    return_err,
    unwrap_or_return,
)

# -----------------------------------------------------------------------------------


def test_exception_as_err_logged() -> None:
    assert fun_with_result(2) == Ok(0.5)
    assert isinstance(
        fun_with_result(0).err(),
        ZeroDivisionError,
    )  # should spam your logs with the zero-division-error!
    assert isinstance(fun_with_result(3).err(), str)  # is NOT spamming your logs


@exceptions_as_err_logged(Exception)
def fun_with_result(x: int) -> Result[float, str]:  # noqa: ARG001
    shit_might_happen = 1 / x
    if x == 3:  # noqa: PLR2004
        return Err("don't like this!")
    return Ok(shit_might_happen)


# -----------------------------------------------------------------------------------


def test_panic_for_violated_inputparams_log_and_return_output_type_violations() -> None:
    with pytest.raises(BeartypeCallHintParamViolation):
        dont_violate_my_params("bad-param")

    output = dont_violate_my_params(
        1,
    )  # this should spam your logs with the beartype-error! but it is not getting raised so one can handle it
    assert isinstance(output.err(), BeartypeCallHintReturnViolation)


@as_result_logged_panic_for_param_violations(Exception)
def dont_violate_my_params(x: int) -> float:
    print(x)  # noqa: T201
    return "bar"


# -----------------------------------------------------------------------------------


def test_early_return() -> None:
    assert early_return(Ok(1)) == Ok(3)
    assert early_return(Err("foo")) == Err("foo")
    with pytest.raises(EarlyReturnError):
        # you are never supposed to see this exception, only if you forgot the decorator!
        forgotten_decorator()


def forgotten_decorator() -> Result[int, str]:
    Err("foo").unwrap_or_else(return_err)
    return Ok(0)


@return_early
def early_return(o: Result[int, str]) -> Result[int, str]:
    x = unwrap_or_return(o)  # same as: o.unwrap_or_else(return_err)
    y = x + 2
    return Ok(y)
