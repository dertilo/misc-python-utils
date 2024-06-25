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

BAD_NUMBER = 3
BAD_NUMBER_ERROR_STR = "don't like this!"


def test_exception_as_err_logged() -> None:
    assert fun_with_result(2) == Ok(0.5)
    assert isinstance(
        fun_with_result(0).err(),
        ZeroDivisionError,
    )  # should spam your logs with the zero-division-error!
    with pytest.raises(BeartypeCallHintParamViolation):
        fun_with_result("bad-param")  # pyright: ignore [reportArgumentType]
    assert (
        fun_with_result(BAD_NUMBER).err() == BAD_NUMBER_ERROR_STR
    )  # is NOT spamming your logs


@exceptions_as_err_logged(Exception, panic_exceptions={BeartypeCallHintParamViolation})
def fun_with_result(x: int) -> Result[float, str]:  # noqa: ARG001
    shit_might_happen = 1 / x
    if x == BAD_NUMBER:  # noqa: PLR2004
        return Err(BAD_NUMBER_ERROR_STR)
    return Ok(shit_might_happen)


# -----------------------------------------------------------------------------------
def test_wrong_expections():  # noqa: ANN201
    with pytest.raises(ValueError):  # noqa: PT011
        exceptions_as_err_logged(
            ZeroDivisionError,
            panic_exceptions={BeartypeCallHintParamViolation},
        )
    with pytest.raises(TypeError):
        exceptions_as_err_logged(BaseException)  # pyright: ignore [reportArgumentType]


# -----------------------------------------------------------------------------------


def test_panic_for_violated_inputparams_log_and_return_output_type_violations() -> None:
    with pytest.raises(BeartypeCallHintParamViolation):
        dont_violate_my_params("bad-param")  # pyright: ignore [reportArgumentType]

    output = dont_violate_my_params(
        1,
    )  # this should spam your logs with the beartype-error! but it is not getting raised so one can handle it
    assert isinstance(output.err(), BeartypeCallHintReturnViolation)


@as_result_logged_panic_for_param_violations(Exception)
def dont_violate_my_params(x: int) -> float:
    print(x)  # noqa: T201
    return "bar"  # pyright: ignore [reportReturnType]


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
