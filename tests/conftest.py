import logging
from pathlib import Path

import pytest

from misc_python_utils.colored_logs_formatter import prepare_logger
from misc_python_utils.prefix_suffix import BASE_PATHES, PrefixSuffix

TEST_RESOURCES = "tests/resources"

# pytest --log-cli-level is not working properly, see: https://stackoverflow.com/questions/52086974/pytest-selective-log-levels-on-a-per-module-basis
prepare_logger("nmaudio", logging.DEBUG)


@pytest.fixture()
def test_resources() -> str:
    return TEST_RESOURCES


@pytest.fixture()
def cache_base(tmp_path: Path) -> PrefixSuffix:
    cache_root = str(tmp_path)
    BASE_PATHES["cache_root"] = cache_root
    return PrefixSuffix("cache_root", "cache_base")
