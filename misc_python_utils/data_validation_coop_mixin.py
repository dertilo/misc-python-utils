from dataclasses import dataclass, field
from typing import final

from result import Err, Ok, Result
from typing_extensions import Self

from misc_python_utils.dataclass_utils import FixedDict


class CoopDataValidationError(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)


@dataclass
class DataValidationCoopMixinBase(FixedDict):
    """
    tilo : not sure yet whether this is a good idea!
    subclasses are supposed to implement a _parse_validate_data method AND call super()._parse_validate_data() at the end!
    """

    _validate_call_chain_worked: bool = field(init=False, repr=False, default=False)

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
