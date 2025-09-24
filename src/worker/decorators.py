from typing import Callable
from functools import wraps
from worker.abc import FunctionWorker


def worker(func: Callable) -> Callable:
    """
    Worker decorator to convert a function into a FunctionWorker.

    Usage:
        @worker
        def add(a: int, b: int) -> int:
            return a + b
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    wrapper.func = func
    wrapper.worker_class = FunctionWorker
    wrapper.create_worker = lambda: FunctionWorker(func)

    return wrapper
