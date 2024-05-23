import dataclasses
import itertools
import logging
import tarfile
from collections.abc import Callable, Iterator
from pathlib import Path

from tqdm import tqdm

from misc_python_utils.prefix_suffix import PrefixSuffix

logger = logging.getLogger(
    __name__,
)  # "The name is potentially a period-separated hierarchical", see: https://docs.python.org/3.10/library/logging.html


@dataclasses.dataclass(slots=True, frozen=True)
class TarFileOutput:
    info: tarfile.TarInfo
    exfile_object: tarfile.ExFileObject


def filter_gen_targz_members(
    targz_file: str | PrefixSuffix,
    is_of_interest_fun: Callable[[tarfile.TarInfo], bool],
    start: int | None = None,
    stop: int | None = None,
    verbose: bool = False,
) -> Iterator[TarFileOutput]:
    with tarfile.open(str(targz_file), "r:gz") as tar:
        g = itertools.islice(tar, start, stop)
        if verbose:
            g = tqdm(g, position=0, desc=f"iterating over {Path(str(targz_file)).name}")
        for member in g:
            member: tarfile.TarInfo
            if is_of_interest_fun(member):
                f: tarfile.ExFileObject | None = tar.extractfile(member)
                # https://stackoverflow.com/questions/37474767/read-tar-gz-file-in-python
                # tarfile.extractfile() can return None if the member is neither a file nor a link.
                neither_file_nor_link = f is None
                if not neither_file_nor_link:
                    yield TarFileOutput(member, f)
