from typing import TypeVar

T = TypeVar("T")


class BaseRegistry[T]:
    """Base registry class for storing and managing objects."""

    def __init__(self):
        self._registry: dict[str, T] = {}

    def register(self, name: str, obj: T) -> None:
        """Register an object with the given name."""
        if self.exists(name):
            raise KeyError(f"{type(obj).__name__} '{name}' already registered")
        self._registry[name] = obj

    def get(self, name: str) -> T:
        """Get an object by name."""
        if not self.exists(name):
            raise KeyError(f"'{name}' not found in registry")
        return self._registry[name]

    def exists(self, name: str) -> bool:
        """Check if an object exists in the registry."""
        return name in self._registry

    def list_names(self) -> list[str]:
        """List all registered names."""
        return list(self._registry.keys())

    def clear(self) -> None:
        """Clear all registered objects."""
        self._registry.clear()

    def __contains__(self, name: str) -> bool:
        """Check if name exists in registry using 'in' operator."""
        return self.exists(name)

    def __len__(self) -> int:
        """Get the number of registered objects."""
        return len(self._registry)
