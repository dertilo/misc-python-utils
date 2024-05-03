from dataclasses import dataclass

import pytest

from misc_python_utils.data_validation_coop_mixin import DataValidationCoopMixinBase

# ----------- following classes are just for testing and show-casing -----------------
@dataclass
class NeStartEnd(DataValidationCoopMixinBase):
    start: float
    end: float

    def _parse_validate_data(self) -> None:
        assert self.end > self.start
        super()._parse_validate_data()


@dataclass
class NeStartEndMs(NeStartEnd):
    def _parse_validate_data(self) -> None:
        self.start = round(self.start * 1000)
        self.end = round(self.end * 1000)
        super()._parse_validate_data()

# -------------------------------------------------------------------------------------

def test_datavalidation_coop_mixin():
    NeStartEnd(1.0, 2.0)
    with pytest.raises(AssertionError):
        NeStartEnd(2.0, 1.0)

    with pytest.raises(AssertionError):
        NeStartEndMs(0.0, 0.000_1)
