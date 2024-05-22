import itertools
import json
from collections.abc import Callable, Iterable, Iterator
from typing import Any

from misc_python_utils.file_utils.readwrite_files import (
    FilePath,
    read_lines,
    write_lines,
)


def write_dicts_to_csv(
    file: FilePath,
    data: Iterable[dict[str, Any]],
    header: list[str] | None = None,
    delimiter: str = "\t",
) -> None:
    def gen_rows(header: list[str] | None) -> Iterator[str]:
        if header is not None:
            yield delimiter.join(header)
        for datum in data:
            if header is None:
                header = list(datum.keys())
                yield delimiter.join(header)
            csv_row = build_csv_row([datum.get(k, None) for k in header])
            yield csv_row

    write_lines(file, gen_rows(header))


def build_csv_row(datum: list[Any], delimiter: str = "\t") -> str:
    line = (
        json.dumps(datum, ensure_ascii=False)
        .replace("[", "")
        .replace(
            "]",
            "",
        )
    )
    cols = [s.strip(" ") for s in line.split(",") if len(s) > 0]
    return delimiter.join(cols)


def write_csv(
    file: FilePath,
    data: Iterable[list[Any]],
    header: list[str] | None = None,
    delimiter: str = "\t",
) -> None:
    file = str(file)
    write_lines(
        file,
        itertools.chain(
            [delimiter.join(header)] if header is not None else [],
            (build_csv_row(d, delimiter=delimiter) for d in data),
        ),
    )


def read_csv(  # noqa: PLR0913
    file_path: str,
    delimiter: str = "\t",
    encoding: str = "utf-8",
    use_json_loads: bool = True,
    process_row: Callable[[list[Any]], list[Any]] = lambda x: x,
    keys: list[str] | None = None,
) -> Iterable[dict[str, Any]]:  # TODO: json.loads should recognize int/float
    lines = read_lines(file_path, encoding=encoding)
    yield from read_csv_lines(
        lines,
        delimiter,
        use_json_loads=use_json_loads,
        process_row=process_row,
        keys=keys,
    )


def read_csv_lines(
    lines: Iterable[str],
    delimiter: str,
    use_json_loads: bool = True,
    process_row: Callable[[list[Any]], list[Any]] = lambda x: x,
    keys: list[str] | None = None,
) -> Iterable[dict[str, Any]]:
    if use_json_loads:

        def process_fun(row: list[str]) -> list[Any]:
            s = f'[{",".join(row)}]'
            return json.loads(s)

        process_row = process_fun

    it = iter(lines)
    header = [h for h in next(it).replace("\r", "").split(delimiter) if len(h) > 0]
    if keys is not None:
        assert len(header) == len(keys)
        header = keys
    for l in it:
        row = l.replace("\r", "").split(delimiter)
        row = process_row(row)
        assert len(row) == len(header), f"{header=}, {row=}"
        yield {col: row[k] for k, col in enumerate(header)}
