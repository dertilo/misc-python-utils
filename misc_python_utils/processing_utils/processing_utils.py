import collections  # noqa: F401
import logging
import subprocess
from collections.abc import Callable, Iterable, Iterator
from concurrent import futures as cf
from typing import TypeVar

logger = logging.getLogger(
    __name__,
)  # "The name is potentially a period-separated hierarchical", see: https://docs.python.org/3.10/library/logging.html


def exec_command(command: str) -> tuple[list, list]:
    with subprocess.Popen(
        command,
        shell=True,  # noqa: S602 -> TODO: shell=True is insecure?
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ) as p:
        stdout, stderr = p.stdout.readlines(), p.stderr.readlines()
    return stdout, stderr  # noqa: TMN002 TODO: wtf!!


def exec_command_yield_stdout(command: str) -> Iterator[str]:
    with subprocess.Popen(
        command,
        shell=True,  # noqa: S602
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ) as p:
        while p.poll() is None:
            for l in iter(p.stdout.readline, ""):
                yield l.decode("utf-8").rstrip()

            for l in iter(p.stderr.readline, ""):
                logger.error(l.decode("utf-8").rstrip())


T = TypeVar("T")


def iterable_to_batches(g: Iterable[T], batch_size: int) -> Iterator[list[T]]:
    batch = []
    for element in g:
        batch.append(element)
        if len(batch) == batch_size:
            yield batch
            batch = []
    if len(batch) > 0:
        yield batch


Tout = TypeVar("Tout")


def process_with_threadpool(
    data: list,
    process_fun: Callable,
    max_workers: int = 1,
    timeout: float | None = None,
) -> Iterator[Tout]:
    """see: https://docs.python.org/3/library/concurrent.futures.html"""
    with cf.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_sample = [executor.submit(process_fun, d) for d in data]
        for future in cf.as_completed(future_to_sample, timeout=timeout):
            yield future.result()
