import bz2
import gzip
import json
import locale
from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

assert locale.getpreferredencoding(False) == "UTF-8"

FilePath = str | Path


def write_jsonl(
    file: FilePath,
    data: Iterable[dict | (list | tuple)],
    mode: str = "w",  # str
    do_flush: bool = False,
) -> None:
    file = str(file)

    def process_line(d: dict) -> str | bytes:
        line = json.dumps(d, skipkeys=True, ensure_ascii=False)
        line = line + "\n"
        return line.encode("utf-8")

    with writable(file, mode) as f:
        f.writelines(process_line(d) for d in data)
        if do_flush:
            f.flush()


def write_json(
    file: FilePath,
    datum: dict,
    mode: str = "w",
    do_flush: bool = False,
    indent: int | None = None,  # use indent =4 for "pretty json"
) -> None:
    file = str(file)
    with writable(file, mode) as f:
        line = json.dumps(datum, skipkeys=True, ensure_ascii=False, indent=indent)
        line = line.encode("utf-8")
        f.write(line)
        if do_flush:
            f.flush()


def write_file(
    file: FilePath,
    s: str,
    mode: str = "w",
    do_flush: bool = False,
) -> None:
    file = str(file)
    with writable(file, mode) as f:
        f.write(s.encode("utf-8"))
        if do_flush:
            f.flush()


def read_file(file: FilePath, encoding: str = "utf-8") -> str:
    file = str(file)
    file_io_supplier = lambda: (
        gzip.open(file, mode="r", encoding=encoding)
        if file.endswith(".gz")
        else open(file, encoding=encoding)  # noqa: PTH123, SIM115
    )
    with file_io_supplier() as f:
        return f.read()


def write_lines(
    file: FilePath,
    lines: Iterable[str],
    mode: str = "w",
) -> None:
    file = str(file)

    def process_line(line: str) -> str | bytes:
        line = line + "\n"
        return line.encode("utf-8")

    with writable(file, mode) as f:
        f.writelines(process_line(l) for l in lines)


@contextmanager
def writable(  # noqa: ANN201
    file: str,
    mode: str = "w",
):  # python 3.10 does not like this type-hint (it works for 3.12): Iterator[TextIO | gzip.GzipFile]
    mode += "b"
    if file.endswith(".gz"):
        with open(file, mode=mode) as f:  # noqa: SIM117, PTH123
            # exlcuding timestamp from gzip, see: https://stackoverflow.com/questions/25728472/python-gzip-omit-the-original-filename-and-timestamp

            with gzip.GzipFile(fileobj=f, mode=mode, filename="", mtime=0) as fgz:
                yield fgz
    else:
        with open(file, mode=mode) as f:  # noqa: PTH123
            yield f


def read_jsonl(
    file: FilePath,
    encoding: str = "utf-8",
    limit: int | None = None,
    num_to_skip: int = 0,
) -> Iterator[dict[str, Any]]:
    for l in read_lines(file, encoding, limit, num_to_skip):
        yield json.loads(l)


def read_lines(  # noqa: WPS231
    file: FilePath,
    encoding: str = "utf-8",
    limit: int | None = None,
    num_to_skip: int = 0,
) -> Iterator[str]:
    file = str(file)
    mode = "rb"
    open_methods = {
        "gz": lambda f: gzip.open(f, mode=mode),
        "bz2": lambda f: bz2.open(f, mode=mode),
    }
    file_io_supplier = open_methods.get(
        file.split(".")[-1].lower(),
        lambda f: open(f, mode=mode),  # noqa: PTH123, SIM115
    )

    with file_io_supplier(file) as f:
        _ = [next(f) for _ in range(num_to_skip)]
        for counter, raw_line in enumerate(f):
            if limit is not None and (counter >= limit):
                break
            line = raw_line.decode(encoding) if "b" in mode else raw_line
            line = line.replace("\n", "").replace("\r", "")
            yield line


def read_json(file: FilePath, mode: str = "b") -> dict:
    file = str(file)
    with gzip.open(file, mode="r" + mode) if file.endswith(
        "gz"  # noqa: COM812
    ) else open(  # noqa: PTH123
        file,
        mode="r" + mode,
    ) as f:
        s = f.read()
        s = s.decode("utf-8") if mode == "b" else s
        return json.loads(s)
