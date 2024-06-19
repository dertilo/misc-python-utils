import json
import operator
from typing import Any

from misc_python_utils.dict_utils import flatten_nested_dict, nest_flattened_dict
from misc_python_utils.utils import (
    collapse_sequence,
    just_try,
    sanitize_hexappend_filename,
    sorted_groupby,
)


def test_just_try():  # noqa: ANN201
    o = just_try(lambda: 42, default="foo")
    assert o == 42  # noqa: PLR2004

    o = just_try(lambda: 1 / 0, default="foo")
    assert o == "foo"


def test_file_name() -> None:
    filename = "ad\n bla/'{-+\)_(ç?"
    sane_filename = sanitize_hexappend_filename(filename)
    print(sane_filename)  # noqa: T201


def test_flatten_nested_dict() -> None:
    expected = {
        "a": {"a": 1.2, "b": "foo-4", "k": 4},
        "b": {"a": 1.2, "b": {"a": 1.2, "b": "foo-4", "k": 4}, "k": 4},
        "k": 3,
    }
    flattened_dict = flatten_nested_dict(expected)
    nested_dict = nest_flattened_dict(flattened_dict)
    assert nested_dict == expected, f"{nested_dict}!={expected}"


def test_collapse_sequence() -> None:
    input_ = [
        ("a", 1),
        ("a", 1),
        ("b", 1),
        ("a", 1),
        ("c", 1),
        ("c", 1),
        ("c", 1),
    ]
    expected = [("a", 2), ("b", 1), ("a", 1), ("c", 3)]
    collapsed = collapse_sequence(
        input_,
        merge_fun=lambda gr: sum(x for _, x in gr),
        get_key_fun=operator.itemgetter(0),
    )
    assert json.dumps([(o.key, o.value) for o in collapsed]) == json.dumps(expected)


def test_group_dicts(  # noqa: ANN201
    data=None,  # noqa: ANN001
):
    if data is None:
        data = [
            {"foo": "bar", "jon": 1},
            {"foo": "bar", "jon": 2},
            {"foo": "foobar", "jon": 3},
        ]

    def get_groupby_val(d: dict[str, Any]) -> str:
        return d["foo"]

    key2group = sorted_groupby(data, get_groupby_val)
    assert key2group == {
        "bar": [{"foo": "bar", "jon": 1}, {"foo": "bar", "jon": 2}],
        "foobar": [{"foo": "foobar", "jon": 3}],
    }
