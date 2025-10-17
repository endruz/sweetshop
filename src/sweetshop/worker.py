from collections.abc import Callable
from typing import TYPE_CHECKING, Generic, Type

from sweetshop.base_data import BaseData, TData
from sweetshop.registry import BaseRegistry

if TYPE_CHECKING:
    from sweetshop.pipe import Node


class Worker(Generic[TData]):
    def __init__(
        self, func: Callable, name: str | None = None, data_type: Type[TData] = None
    ):
        if data_type is None:
            raise ValueError("'data_type' must be provided for Worker")
        if not isinstance(data_type, type) or not issubclass(data_type, BaseData):
            raise TypeError("'data_type' must be a subclass of BaseData")

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
        if not args or not isinstance(args[0], self.data_type):
            raise TypeError(
                f"Expected first argument of type {self.data_type.__name__}, "
                f"got {type(args[0]).__name__ if args else 'None'}"
            )
        result = self.func(*args, **kwargs)
        if not isinstance(result, self.data_type):
            raise TypeError(
                f"Expected return value of type {self.data_type.__name__}, "
                f"got {type(result).__name__}"
            )
        return result

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
