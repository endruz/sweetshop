from typing import Any

from collections.abc import Callable


class Worker:
    def __init__(self, func: Callable, name: str | None = None):
        self.name: str = name or getattr(func, "__name__", "unknown_function")
        self.func: Callable = func
        self.error: Exception | None = None

    def execute(self, *args, **kwargs) -> Any:
        return self.func(*args, **kwargs)

    def run(self, *args, **kwargs) -> Any:
        try:
            result: Any = self.execute(*args, **kwargs)
            return result
        except Exception as e:
            self.error = e
            raise

    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}')"

    @staticmethod
    def create(name: str | None = None) -> Callable:
        def wrapper(func: Callable) -> "Worker":
            return Worker(func, name)

        return wrapper
