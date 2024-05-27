from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from misc_python_utils.beartypes import NeList, NeStr
from misc_python_utils.dict_utils import _NOT_EXISTING

# TODO: move this elsewhere! it is not realated to mermaid-stuff!


def format_table_cell(v: float | Any, formatt: str = ".2f") -> str:
    if isinstance(v, float):
        v = f"{v:{formatt}}"
    if isinstance(v, _NOT_EXISTING):
        v = None
    return f"{v}"


@dataclass
class TableHeaders:
    row_title: NeStr
    col_title: NeStr
    row_names: NeList[NeStr]
    col_names: NeList[NeStr]


def build_markdown_table(
    rows: list[list[Any]],
    table_headers: TableHeaders,
    format_fun: Callable[[Any], str] = format_table_cell,
) -> str:
    th = table_headers
    rows_s = [[format_fun(v) for v in r] for r in rows]
    header = " | ".join([f"{th.row_title} \ {th.col_title}", *th.col_names])
    line = " | ".join(["---" for _ in range(len(th.col_names) + 1)])
    rows = [
        " | ".join([name, *cols])
        for name, cols in zip(th.row_names, rows_s, strict=True)
    ]
    return "\n".join([header, line, *rows])


def build_markdown_table_from_dicts(
    dicts: NeList[dict[str, float]],
    col_title: str | None = None,
    col_names: NeList[str] | None = None,
    format_fun: Callable[[Any], str] = format_table_cell,
) -> str:
    if col_names is None:
        col_names = list(dicts[0].keys())

    row_title = col_names[0]
    rows_s = [[format_fun(d.get(c, None)) for c in col_names] for d in dicts]
    col_title = f" \ {col_title}" if col_title is not None else ""
    header = " | ".join([f"{row_title}{col_title}"] + col_names[1:])
    line = " | ".join(["---" for _ in range(len(col_names))])
    rows = [" | ".join(row) for row in rows_s]
    return "\n".join([header, line, *rows])
