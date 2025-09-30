"""Tests for registry module."""

import pytest

from sweetshop.registry import BaseRegistry


class RegistryTestItem:
    """Test item class for registry testing."""

    def __init__(self, name: str, value: int):
        self.name = name
        self.value = value

    def __repr__(self):
        return f"TestItem(name='{self.name}', value={self.value})"


class TestBaseRegistry:
    """Test cases for BaseRegistry class."""

    def setup_method(self):
        """Set up test registry for each test."""
        self.registry = BaseRegistry[RegistryTestItem]()
        self.item1 = RegistryTestItem("item1", 10)
        self.item2 = RegistryTestItem("item2", 20)

    def test_registry_creation(self):
        """Test creating a new registry."""
        registry = BaseRegistry[RegistryTestItem]()
        assert len(registry) == 0
        assert list(registry.list_names()) == []

    def test_register_item(self):
        """Test registering an item."""
        self.registry.register("test_item", self.item1)
        assert self.registry.exists("test_item")
        assert len(self.registry) == 1
        assert "test_item" in self.registry.list_names()

    def test_register_duplicate_item(self):
        """Test registering duplicate item raises KeyError."""
        self.registry.register("test_item", self.item1)
        with pytest.raises(
            KeyError,
            match="RegistryTestItem 'test_item' already registered",
        ):
            self.registry.register("test_item", self.item2)

    def test_get_item(self):
        """Test getting a registered item."""
        self.registry.register("test_item", self.item1)
        retrieved_item = self.registry.get("test_item")
        assert retrieved_item is self.item1
        assert retrieved_item.name == "item1"
        assert retrieved_item.value == 10

    def test_get_nonexistent_item(self):
        """Test getting non-existent item raises KeyError."""
        with pytest.raises(KeyError, match="'nonexistent' not found in registry"):
            self.registry.get("nonexistent")

    def test_exists(self):
        """Test checking if item exists."""
        assert not self.registry.exists("test_item")
        self.registry.register("test_item", self.item1)
        assert self.registry.exists("test_item")

    def test_list_names(self):
        """Test listing all registered names."""
        assert self.registry.list_names() == []

        self.registry.register("item1", self.item1)
        self.registry.register("item2", self.item2)

        names = self.registry.list_names()
        assert len(names) == 2
        assert "item1" in names
        assert "item2" in names

    def test_clear(self):
        """Test clearing all registered items."""
        self.registry.register("item1", self.item1)
        self.registry.register("item2", self.item2)
        assert len(self.registry) == 2

        self.registry.clear()
        assert len(self.registry) == 0
        assert self.registry.list_names() == []
        assert not self.registry.exists("item1")
        assert not self.registry.exists("item2")

    def test_contains_operator(self):
        """Test using 'in' operator to check existence."""
        assert "test_item" not in self.registry
        self.registry.register("test_item", self.item1)
        assert "test_item" in self.registry

    def test_len_operator(self):
        """Test using len() to get registry size."""
        assert len(self.registry) == 0

        self.registry.register("item1", self.item1)
        assert len(self.registry) == 1

        self.registry.register("item2", self.item2)
        assert len(self.registry) == 2

        self.registry.clear()
        assert len(self.registry) == 0

    def test_multiple_registries_independent(self):
        """Test that multiple registry instances are independent."""
        registry1 = BaseRegistry[RegistryTestItem]()
        registry2 = BaseRegistry[RegistryTestItem]()

        registry1.register("item1", self.item1)
        registry2.register("item2", self.item2)

        assert registry1.exists("item1")
        assert not registry1.exists("item2")
        assert registry2.exists("item2")
        assert not registry2.exists("item1")

        assert len(registry1) == 1
        assert len(registry2) == 1


if __name__ == "__main__":
    pytest.main([__file__])
