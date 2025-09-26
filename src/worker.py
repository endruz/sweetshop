from typing import Any

from collections.abc import Callable
from registry import BaseRegistry


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


class WorkerRegistry(BaseRegistry[Worker]):
    """Registry for managing Worker instances."""

    def register(self, name: str, worker: Worker) -> None:
        """Register a worker with the given name."""
        if self.exists(name):
            raise KeyError(f"Worker '{name}' already registered")
        super().register(name, worker)

    def __getattr__(self, name: str) -> Worker:
        """Allow accessing workers as attributes for createnode() calls."""
        if self.exists(name):
            return self._registry[name]
        raise AttributeError(f"Worker '{name}' not found in registry")

    def register_worker(self, name: str | None = None) -> Callable:
        def wrapper(func: Callable) -> Callable:
            worker = Worker(func, name)
            self.register(worker.name, worker)
            return func

        return wrapper


# Global worker registry instance
worker_registry = WorkerRegistry()
