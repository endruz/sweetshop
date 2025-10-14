import pytest

from sweetshop import Worker, WorkerRegistry
from tests.common.digital_data import DigitalData


class TestWorkerRegistry:
    """Test cases for WorkerRegistry class."""

    def setup_method(self):
        """Set up test registry for each test."""
        self.registry = WorkerRegistry()

    def test_registry_creation(self):
        """Test creating a new worker registry."""
        registry = WorkerRegistry()
        assert len(registry) == 0

    def test_register_worker_decorator(self):
        """Test registering worker using decorator."""

        @self.registry.register_worker(data_type=DigitalData)
        def test_function():
            return DigitalData(123)

        assert self.registry.exists("test_function")
        worker = self.registry.get("test_function")
        assert isinstance(worker, Worker)
        assert worker.name == "test_function"
        assert worker.data_type == DigitalData

    def test_register_worker_decorator_custom_name(self):
        """Test registering worker with custom name."""

        @self.registry.register_worker(data_type=DigitalData, name="custom_worker")
        def test_function():
            return DigitalData(456)

        assert self.registry.exists("custom_worker")
        assert not self.registry.exists("test_function")
        worker = self.registry.get("custom_worker")
        assert isinstance(worker, Worker)
        assert worker.name == "custom_worker"
        assert worker.data_type == DigitalData

    def test_getattr_access(self):
        """Test accessing workers via attribute access."""

        @self.registry.register_worker(data_type=DigitalData)
        def my_worker():
            return DigitalData(789)

        # Test attribute access
        worker = self.registry.my_worker
        assert isinstance(worker, Worker)
        assert worker.name == "my_worker"

    def test_getattr_nonexistent_worker(self):
        """Test accessing non-existent worker raises AttributeError."""
        with pytest.raises(
            AttributeError, match="Worker 'nonexistent' not found in registry"
        ):
            _ = self.registry.nonexistent

    def test_register_worker_decorator_returns_original_function(self):
        """Test that decorator returns the original function."""

        def original_function():
            return DigitalData(999)

        decorated = self.registry.register_worker(data_type=DigitalData)(
            original_function
        )
        assert decorated == original_function

    def test_multiple_workers_registration(self):
        """Test registering multiple workers."""

        @self.registry.register_worker(data_type=DigitalData)
        def worker1():
            return DigitalData(1)

        @self.registry.register_worker(data_type=DigitalData)
        def worker2():
            return DigitalData(2)

        assert len(self.registry) == 2
        assert self.registry.exists("worker1")
        assert self.registry.exists("worker2")

        w1 = self.registry.worker1
        w2 = self.registry.worker2
        assert w1.execute().value == 1
        assert w2.execute().value == 2


if __name__ == "__main__":
    pytest.main([__file__])
