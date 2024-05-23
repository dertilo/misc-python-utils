from collections.abc import Callable, Iterable, Iterator
from concurrent import futures as cf
from concurrent.futures import FIRST_COMPLETED, Future, wait
from typing import TypeVar

from misc_python_utils.processing_utils.processing_utils import iterable_to_batches

Tin = TypeVar("Tin")
Tout = TypeVar("Tout")

POISON_PILL = "<POISON_PILL>"


def process_with_threadpool_backpressure(
    process_batch_fun: Callable[[list[Tin]], Tout],
    data: Iterable,
    max_workers: int = 1,
    batch_size: int = 1,
) -> Iterator[Tout]:
    # TODO: stupid multiprocessing Pool does not know back-pressure!!!
    # see: https://stackoverflow.com/questions/30448267/multiprocessing-pool-imap-unordered-with-fixed-queue-size-or-buffer
    # TODO: not yet tested!

    it = iter(data)
    it = iter(iterable_to_batches(data, batch_size=batch_size))

    with cf.ThreadPoolExecutor(max_workers=max_workers) as executor:

        def gen_futures(num_new_jobs: int) -> Iterator[Future | str]:
            for _ in range(num_new_jobs):
                try:
                    next_job = next(it)
                    yield executor.submit(process_batch_fun, next_job)
                except StopIteration:  # noqa: PERF203
                    yield POISON_PILL

        futures = list(gen_futures(max_workers))

        yield from _process_with_backpressure(gen_futures, futures)


def _process_with_backpressure(
    gen_futures: Callable,
    futures: list[Future | str],
) -> Iterator[Tout]:
    def fill_compleded_by_new_jobs(
        completed: list,
        futures,  # noqa: ANN001
    ) -> bool:
        input_is_exhausted = False
        for fu in gen_futures(len(completed)):
            if fu != POISON_PILL:
                futures.add(fu)
            else:
                input_is_exhausted = True
                break
        return input_is_exhausted

    input_is_exhausted = False
    while not input_is_exhausted:
        completed, futures = wait(futures, return_when=FIRST_COMPLETED)

        input_is_exhausted = fill_compleded_by_new_jobs(
            completed,
            futures,
        )
        yield from _yield_results(completed)

    yield from _yield_results(completed=cf.as_completed(futures))


def _yield_results(completed: Iterable[Future]) -> Iterator[Tout]:
    for fu in completed:
        yield fu.result()  # why a yield from? -> cause its processing batches!
