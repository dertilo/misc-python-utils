from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import final

from misc_python_utils.dataclass_utils import FixedDict


class MroDataValidationError(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)


@dataclass
class DataValidationMROMixin(FixedDict, ABC):
    """
    why do I need this fancy cooperative super() -calling?
    if I could just manually loop over the MRO and call the methods?
    """

    @final
    def __post_init__(self):
        self._loop_over_mro()
        super().__post_init__()  # for the FixedDict

    def _loop_over_mro(self) -> None:
        for cls in self.__class__.__mro__:
            if (
                issubclass(cls, DataValidationMROMixin)
                and cls != DataValidationMROMixin
            ):
                cls._parse_validate_data(self)
            else:
                assert cls == DataValidationMROMixin, f"unexpected class: {cls}"
                break

    @abstractmethod
    def _parse_validate_data(self) -> None:
        """
        inheriting classes are supposed to override this method!
        :return:
        """
