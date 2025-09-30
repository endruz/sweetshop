from collections.abc import Callable
from typing import TYPE_CHECKING, Generic, Type

from sweetshop.base_data import TData
from sweetshop.registry import BaseRegistry

if TYPE_CHECKING:
    from sweetshop.pipe import Node


class Worker(Generic[TData]):
    def __init__(
        self, func: Callable, name: str | None = None, data_type: Type[TData] = None
    ):
        self.name: str = name or getattr(func, "__name__", "unknown_worker")
        self.func: Callable = func
        self.data_type: Type[TData] = data_type

    def cfg(self, **kwargs) -> "Node":
        """Create a configured node for this worker"""
        # Import here to avoid circular import
        from sweetshop.pipe import Node

        return Node(self, kwargs)

    def execute(self, *args, **kwargs) -> TData:
        """Execute worker"""
        return self.func(*args, **kwargs)

    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}', type={self.data_type.__name__})"


class WorkerRegistry(BaseRegistry[Worker]):
    """Registry for managing Worker instances."""

    def __getattr__(self, name: str) -> Worker:
        """Allow accessing workers as attributes for createnode() calls."""

        if self.exists(name):
            return self._registry[name]
        raise AttributeError(f"Worker '{name}' not found in registry")

    def register_worker(
        self,
        data_type: Type[TData],
        name: str | None = None,
    ) -> Callable:
        """Register decorator supporting data type constraints"""

        def wrapper(func: Callable) -> Callable:
            worker = Worker(func, name, data_type)
            self.register(worker.name, worker)
            return func

        return wrapper


# Global worker registry instance
worker_registry = WorkerRegistry()
