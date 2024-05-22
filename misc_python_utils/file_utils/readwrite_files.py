import bz2
import gzip
import json
import locale
import typing
from collections import defaultdict
from collections.abc import Callable, Iterable, Iterator
from contextlib import contextmanager
from io import BufferedReader
from pathlib import Path
from typing import IO, TYPE_CHECKING, Any

assert locale.getpreferredencoding(False) == "UTF-8"

FilePath = str | Path


JsonlLine = dict[str, Any] | (list[Any] | tuple[Any, ...])


def write_jsonl(
    file: FilePath,
    data: Iterable[JsonlLine],
    mode: str = "w",  # str
    do_flush: bool = False,
) -> None:
    file = str(file)

    def process_line(d: JsonlLine) -> bytes:
        line = json.dumps(d, skipkeys=True, ensure_ascii=False)
        line = line + "\n"
        return line.encode("utf-8")

    with writable(file, mode) as f:
        f.writelines(process_line(d) for d in data)
        if do_flush:
            f.flush()


def write_json(
    file: FilePath,
    datum: dict[str, Any],
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
        return str(f.read())  # just to make pyright happy


def write_lines(
    file: FilePath,
    lines: Iterable[str],
    mode: str = "w",
) -> None:
    file = str(file)

    def process_line(line: str) -> bytes:
        line = line + "\n"
        return line.encode("utf-8")

    with writable(file, mode) as f:
        f.writelines(process_line(l) for l in lines)


def writable_it(
    file: str,
    mode: str = "w",
) -> typing.Iterator[IO[bytes] | gzip.GzipFile]:
    mode += "b"
    if file.endswith(".gz"):
        with open(file, mode=mode) as f:  # noqa: SIM117, PTH123
            # exlcuding timestamp from gzip, see: https://stackoverflow.com/questions/25728472/python-gzip-omit-the-original-filename-and-timestamp

            with gzip.GzipFile(fileobj=f, mode=mode, filename="", mtime=0) as fgz:
                yield fgz
    else:
        with open(file, mode=mode) as f:  # noqa: PTH123
            yield f


writable = contextmanager(
    writable_it,
)  # avoid beartype-pyright collision by simply not using this type-shifting decorator black-magic!


def read_jsonl(
    file: FilePath,
    encoding: str = "utf-8",
    limit: int | None = None,
    num_to_skip: int = 0,
) -> Iterator[dict[str, Any]]:
    for l in read_lines(file, encoding, limit, num_to_skip):
        yield json.loads(l)


mode = "rb"


def open_fun_supplier() -> Callable[[str], BufferedReader]:
    return lambda f: Path(f).open(mode=mode)  # noqa: SIM115


OPEN_FUNS = Callable[[str], gzip.GzipFile | bz2.BZ2File | BufferedReader]
open_methods: dict[str, OPEN_FUNS] = defaultdict(open_fun_supplier)
open_methods["gz"] = lambda f: gzip.open(f, mode=mode)
open_methods["bz2"] = lambda f: bz2.open(f, mode=mode)


def read_lines(  # noqa: WPS231
    file: FilePath,
    encoding: str = "utf-8",
    limit: int | None = None,
    num_to_skip: int = 0,
) -> Iterator[str]:
    file = str(file)

    file_io_supplier = open_methods[file.split(".")[-1].lower()]

    with file_io_supplier(file) as f:
        _ = [next(f) for _ in range(num_to_skip)]
        for counter, raw_line in enumerate(f):
            if TYPE_CHECKING:
                assert isinstance(raw_line, bytes)  # type-narrowing
            if limit is not None and (counter >= limit):
                break
            line = raw_line.decode(encoding)
            line = line.replace("\n", "").replace("\r", "")
            yield line


def read_json(file: FilePath, mode: str = "b") -> dict[str, Any]:
    file = str(file)
    with gzip.open(file, mode="r" + mode) if file.endswith(
        "gz"  # noqa: COM812
    ) else open(  # noqa: PTH123
        file,
        mode="r" + mode,
    ) as f:
        s = f.read()
        if isinstance(s, bytes):
            s = s.decode("utf-8")
        return json.loads(s)
