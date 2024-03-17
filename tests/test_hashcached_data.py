import tempfile
from dataclasses import dataclass, field
from typing import ClassVar

from misc_python_utils.hashcached_data.hashcached_data import HashCachedData
from misc_python_utils.prefix_suffix import BASE_PATHES, PrefixSuffix

DEFAULT = "<DEFAULT>"

CODE_BASE_STATE = ""


@dataclass
class TestData(HashCachedData):
    test_field: str = field(init=True, repr=True, default=DEFAULT)
    non_init_get_cached: str = field(init=False, repr=True, default=DEFAULT)
    non_repr_not_cached: str = field(init=False, repr=False, default=DEFAULT)
    _with_underscore_is_not_cached: str = field(init=False, repr=True, default=DEFAULT)

    excluded_from_hash_but_still_cached: str = field(
        init=True,
        repr=True,
        default=DEFAULT,
    )
    __exclude_from_hash__: ClassVar[list[str]] = ["excluded_from_hash_but_still_cached"]

    @property
    def name(self):  # noqa: ANN201
        return "test"

    def _build_cache(self):  # noqa: ANN202
        self.non_init_get_cached = dummy_codebase(self.test_field)
        self._with_underscore_is_not_cached = dummy_codebase(self.test_field)
        self.non_repr_not_cached = dummy_codebase(self.test_field)
        self.test_field = dummy_codebase(self.test_field)

    def _load_cached_data(self):  # noqa: ANN202
        super()._load_cached_data()
        self.test_field = dummy_codebase(self.test_field)


VALUE_A = "value-A"
VALUE_B = "value-B"


def test_hash_cached_data():  # noqa: ANN201
    global CODE_BASE_STATE  # noqa: PLW0603
    processed_by_A = dummy_process_fun("A", "bar")

    with tempfile.TemporaryDirectory() as cache_base:
        BASE_PATHES["cache"] = cache_base
        cache_base = PrefixSuffix("cache", "hashcacheddata")  # noqa: PLW2901

        a = TestData(
            test_field="bar",
            cache_base=cache_base,
            excluded_from_hash_but_still_cached=VALUE_A,
        )
        assert a.test_field == "bar"
        CODE_BASE_STATE = "A"
        a.build()
        # dcd=read_json(a.dataclass_json)
        # print(f"{dcd=}")
        assert a.test_field == dummy_process_fun("A", "bar")
        assert a._with_underscore_is_not_cached == processed_by_A  # noqa: SLF001
        assert a.non_init_get_cached == processed_by_A
        assert a.non_repr_not_cached == processed_by_A
        assert a.excluded_from_hash_but_still_cached == VALUE_A
        # code-base changes but hash and cache stay the same!
        CODE_BASE_STATE = "B"
        b = TestData(
            test_field="bar",
            cache_base=cache_base,
            excluded_from_hash_but_still_cached=VALUE_B,
        )
        b.build()
        assert str(a.cache_dir) == str(b.cache_dir)
        # des_dc:TestData=deserialize_dataclass(read_file(str(a.cache_dir)))
        processed_by_A_loaded_by_B = dummy_process_fun("B", processed_by_A)
        assert b.test_field == processed_by_A_loaded_by_B == "B-A-bar"
        assert b.non_init_get_cached == processed_by_A
        assert b._with_underscore_is_not_cached == DEFAULT  # noqa: SLF001
        assert b.non_repr_not_cached == DEFAULT
        assert (
            b.excluded_from_hash_but_still_cached == VALUE_A
        )  # exlcuded but still cached! when loading VALUE_B gets overwritten!


def dummy_codebase(inpt):  # noqa: ANN001, ANN201
    global CODE_BASE_STATE  # noqa: PLW0602
    return dummy_process_fun(CODE_BASE_STATE, inpt)


def dummy_process_fun(code_base_state: str, inpt: str):  # noqa: ANN201
    return f"{code_base_state}-{inpt}"
