import bz2
import gzip
from collections import defaultdict
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from io import BufferedReader
from pathlib import Path
from typing import IO, Literal, TextIO


def writable_it(
    file: str,
    mode: Literal["a", "w"] = "w",
) -> Iterator[IO[bytes] | gzip.GzipFile]:
    mode_b = mode + "b"
    if file.endswith(".gz"):
        with open(file, mode=mode_b) as f:  # noqa: SIM117, PTH123
            # exlcuding timestamp from gzip, see: https://stackoverflow.com/questions/25728472/python-gzip-omit-the-original-filename-and-timestamp

            with gzip.GzipFile(fileobj=f, mode=mode_b, filename="", mtime=0.0) as fgz:
                yield fgz
    else:
        with open(file, mode=mode_b) as f:  # noqa: PTH123
            yield f


writable = contextmanager(
    writable_it,
)  # avoid beartype-pyright collision by simply not using this type-shifting decorator black-magic!
mode = "rb"


def open_fun_supplier() -> Callable[[str], BufferedReader]:
    return lambda f: Path(f).open(mode=mode)  # noqa: SIM115  # pyright: ignore [reportReturnType]


OPEN_FUNS = Callable[[str], gzip.GzipFile | bz2.BZ2File | BufferedReader | TextIO]
OPEN_METHODS: dict[str, OPEN_FUNS] = defaultdict(open_fun_supplier)
OPEN_METHODS["gz"] = lambda f: gzip.open(f, mode=mode)
OPEN_METHODS["bz2"] = lambda f: bz2.open(f, mode=mode)
