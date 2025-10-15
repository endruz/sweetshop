import pytest

from sweetshop import Pipe, PipeRegistry, Worker, worker_registry
from tests.common.digital_data import DigitalData, add_one, add_value, multiply_by_two


class TestPipeRegistry:
    """Test cases for PipeRegistry class."""

    def setup_method(self):
        """Set up test registry for each test."""
        self.registry = PipeRegistry()
        worker_registry.register("add_one", Worker(add_one, data_type=DigitalData))
        worker_registry.register("add_value", Worker(add_value, data_type=DigitalData))
        worker_registry.register(
            "multiply_by_two",
            Worker(multiply_by_two, data_type=DigitalData),
        )

    def teardown_method(self):
        """Tear down after each test."""
        worker_registry.clear()

    def test_registry_creation(self):
        """Test creating a new pipe registry."""
        registry = PipeRegistry()
        assert len(registry) == 0

    def test_register_pipe_decorator(self):
        """Test registering pipe using decorator."""

        @self.registry.register_pipe()
        def test_pipe():
            pipe = Pipe(data_type=DigitalData)
            pipe.start_with(worker_registry.add_one.cfg())
            return pipe

        assert self.registry.exists("test_pipe")
        pipe = self.registry.get("test_pipe")
        assert isinstance(pipe, Pipe)

    def test_register_pipe_decorator_custom_name(self):
        """Test registering pipe with custom name."""

        @self.registry.register_pipe(name="custom_pipe")
        def test_pipe():
            pipe = Pipe(data_type=DigitalData)
            pipe.start_with(worker_registry.add_one.cfg())
            return pipe

        assert self.registry.exists("custom_pipe")
        assert not self.registry.exists("test_pipe")
        pipe = self.registry.get("custom_pipe")
        assert isinstance(pipe, Pipe)

    def test_getattr_access(self):
        """Test accessing pipes via attribute access."""

        @self.registry.register_pipe()
        def test_pipe():
            pipe = Pipe(data_type=DigitalData)
            pipe.start_with(worker_registry.add_one.cfg())
            return pipe

        # Test attribute access
        pipe = self.registry.test_pipe
        assert isinstance(pipe, Pipe)

    def test_getattr_nonexistent_pipe(self):
        """Test accessing non-existent pipe raises AttributeError."""
        with pytest.raises(
            AttributeError, match="Pipe 'nonexistent' not found in registry"
        ):
            _ = self.registry.nonexistent


if __name__ == "__main__":
    pytest.main([__file__])
