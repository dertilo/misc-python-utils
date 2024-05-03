from dataclasses import dataclass

import pytest

from misc_python_utils.data_validation_coop_mixin import CoopMixinBase


@dataclass
class StartEnd(CoopMixinBase):
    start: float
    end: float

    def _parse_validate_data(self) -> None:
        assert self.end >= self.start
        super()._parse_validate_data()


def test_datavalidation_coop_mixin():
    StartEnd(1.0, 2.0)
    with pytest.raises(AssertionError):
        StartEnd(2.0, 1.0)
