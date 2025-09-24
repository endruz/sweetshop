from abc import ABC, abstractmethod
from typing import Any, Callable
from datetime import datetime


class BaseWorker(ABC):
    def __init__(self, name: str | None = None):
        self.name = name or self.__class__.__name__
        self.inputs: dict[str, Any] = {}
        self.outputs: dict[str, Any] = {}
        self.execution_time: datetime | None = None
        self.error: Exception | None = None

    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """core execution logic"""
        pass

    def run(self, *args, **kwargs) -> Any:
        self.execution_time = datetime.now()
        self.inputs = {"args": args, "kwargs": kwargs}

        try:
            result: Any = self.execute(*args, **kwargs)
            self.outputs = {"result": result}
            return result
        except Exception as e:
            self.error = e
            raise

    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}')"


class FunctionWorker(BaseWorker):
    def __init__(self, func: Callable, name: str | None = None):
        name: str = (
            getattr(func, "__name__", "unknown_function") if name is None else name
        )
        super().__init__(name)
        self.func = func

    def execute(self, *args, **kwargs) -> Any:
        return self.func(*args, **kwargs)
