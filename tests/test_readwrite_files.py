import json
import os.path
import shutil
from collections.abc import Callable, Iterable
from typing import Any

from misc_python_utils.dict_utils import flatten_nested_dict
from misc_python_utils.file_utils.readwrite_csv_files import (
    read_csv,
    write_csv,
    write_dicts_to_csv,
)
from misc_python_utils.file_utils.readwrite_files import read_jsonl, write_lines
from misc_python_utils.utils import sanitize_hexappend_filename


def test_reading_jsonl() -> None:
    data = list(read_jsonl("tests/resources/test.jsonl", limit=3, num_to_skip=2))
    expected = [
        {"a": 1.2, "b": "foo-2", "k": 2},
        {"a": 1.2, "b": "foo-3", "k": 3},
        {"a": 1.2, "b": "foo-4", "k": 4},
    ]
    assert all((e == o for e, o in zip(expected, data)))  # noqa: B905


# def read_flattened_csvs(directory: str):
#     g = (l.split("\t") for l in read_lines(f"{directory}/path2filename.csv"))
#     path2filename = {path_s: filename for path_s, filename in g}
#     filename2path = {
#         filename: json.loads(path_s) for path_s, filename in path2filename.items()
#     }
# TODO:


def test_dict_to_csvs() -> None:
    expected = [
        {"a": 1.2, "b": "foo-2", "k": 2},
        {
            "a": {"a": 1.2, "b": "foo-4", "k": 4},
            "b": {"a": 1.2, "b": {"a": 1.2, "b": "foo-4", "k": 4}, "k": 4},
            "k": 3,
        },
        {"a": 1.2, "b": {"a": 1.2, "b": "foo-4", "k": 4}, "k": 4},
    ]
    test_dir = "/tmp/test_csvs"  # noqa: S108
    shutil.rmtree(test_dir, ignore_errors=True)
    flatten_write_to_csvs(test_dir, expected)


def flatten_write_to_csvs(
    directory: str,
    data: Iterable[dict[str, Any]],
    get_id_fun: Callable[[dict[str, Any]], str] | None = None,
) -> None:
    """
    data: iterable of nested dicts
    get_id_fun=lambda d:d["id"]
    """
    os.makedirs(directory, exist_ok=False)  # noqa: PTH103

    path2filename_file = f"{directory}/path2filename.csv"
    path2filename = {}
    for i, d in enumerate(data):
        eid = get_id_fun(d) if get_id_fun is not None else str(i)
        path_values = flatten_nested_dict(d)
        for path, value in path_values:
            path_s = json.dumps(path)
            filename = sanitize_hexappend_filename(path_s)

            if path_s not in path2filename:
                path2filename[path_s] = filename
                write_lines(path2filename_file, [f"{path_s}\t{filename}"], mode="a")

            csv_file = f"{directory}/{filename}.csv"
            write_lines(csv_file, [f"{eid}\t{value}"], mode="a")


def test_read_csv() -> None:
    expected_data = [{"foo": f"foo-{k}", "bar": k} for k in range(3)]
    header = ["foo", "bar"]
    test_file = "/tmp/test.csv"  # noqa: S108
    write_csv(
        test_file,
        data=([d[col] for col in header] for d in expected_data),
        header=header,
    )
    data = list(read_csv(test_file))
    assert data == expected_data


def test_write_dicts_to_csv() -> None:
    expected_data = [{"foo": f"foo-{k}", "bar": k} for k in range(3)]
    test_file = "/tmp/test.csv"  # noqa: S108
    write_dicts_to_csv(
        test_file,
        data=expected_data,
    )
    data = list(read_csv(test_file))
    assert data == expected_data
