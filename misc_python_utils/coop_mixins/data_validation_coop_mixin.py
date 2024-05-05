from dataclasses import dataclass, field
from typing import final

from result import Err, Ok, Result
from typing_extensions import Self

from misc_python_utils.dataclass_utils import FixedDict


class CoopDataValidationError(ValueError):
    def __init__(self, msg: str):
        super().__init__(msg)


@dataclass
class DataValidationCoopMixinBase(FixedDict):
    """
    the cooperative calls to super() are not strictly following the MRO,
     cause you can call them before, inbetween or after your subclasses-validation code and thereby change the order of validation!
     misc_python_utils/data_validation_mro_mixin.py strictly follows the MRO -> less flexible

    subclasses are supposed to implement a _parse_validate_data method AND call super()._parse_validate_data() at the end!
    see: https://sorokin.engineer/posts/en/python_super.html

    """

    _validate_call_chain_worked: bool = field(
        init=False,
        repr=False,
        default=False,
    )  # TODO: this does not guarantee that all subclasses were cooperative!

    @final
    def __post_init__(self):
        self._validate_call_chain_worked = False
        self._parse_validate_data()
        assert self._validate_call_chain_worked
        super().__post_init__()

    def _parse_validate_data(self) -> None:
        """
        inheriting classes are supposed to override this method!
        :return:
        """
        self._validate_call_chain_worked = True


@dataclass
class DataValidationCoopMixinBaseWithResult(FixedDict):
    _validate_call_chain_worked: bool = field(init=False, repr=False, default=False)

    @final
    def parse_validate_as_result(self) -> Result[Self, str]:
        self._validate_call_chain_worked = False
        try:
            self._parse_validate_data()
        except CoopDataValidationError as e:
            return Err(str(e))

        assert self._validate_call_chain_worked
        return Ok(self)

    def _parse_validate_data(self) -> None:
        """
        inheriting classes are supposed to override this method!
        :return:
        """
        self._validate_call_chain_worked = True
