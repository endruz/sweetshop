import pytest

from sweetshop import BaseData, Node, Worker


class DummyData(BaseData):
    """Dummy data class for worker testing."""

    def __init__(self, value: int):
        super().__init__()
        self.value = value

    def __repr__(self):
        return f"DummyData(value={self.value})"

    def __eq__(self, other):
        return isinstance(other, DummyData) and self.value == other.value


def func_without_args() -> DummyData:
    """Simple test function."""
    return DummyData(42)


def func_with_args(data: DummyData, multiplier: int) -> DummyData:
    """Function that takes arguments."""
    return DummyData(data.value * multiplier)


class TestWorker:
    """Test cases for Worker class."""

    def test_worker_creation_with_defaults(self):
        """Test creating worker with default name."""
        worker = Worker(func_without_args, data_type=DummyData)
        assert worker.name == "func_without_args"
        assert worker.func == func_without_args
        assert worker.data_type == DummyData

    def test_worker_creation_with_custom_name(self):
        """Test creating worker with custom name."""
        worker = Worker(func_without_args, name="custom_name", data_type=DummyData)
        assert worker.name == "custom_name"
        assert worker.func == func_without_args
        assert worker.data_type == DummyData

    def test_worker_creation_with_lambda(self):
        """Test creating worker with lambda function."""

        lambda_func = lambda: DummyData(99)  # noqa: E731

        worker = Worker(lambda_func, name="lambda_worker", data_type=DummyData)
        assert worker.name == "lambda_worker"
        assert worker.func == lambda_func

    def test_worker_execute_no_args(self):
        """Test executing worker with no arguments."""
        worker = Worker(func_without_args, data_type=DummyData)
        result = worker.execute()
        assert isinstance(result, DummyData)
        assert result.value == 42

    def test_worker_execute_with_args(self):
        """Test executing worker with arguments."""
        worker = Worker(func_with_args, data_type=DummyData)
        data = DummyData(10)
        result = worker.execute(data, 3)
        assert isinstance(result, DummyData)
        assert result.value == 30

    def test_worker_execute_with_kwargs(self):
        """Test executing worker with keyword arguments."""
        worker = Worker(func_with_args, data_type=DummyData)
        data = DummyData(5)
        result = worker.execute(data, multiplier=4)
        assert result.value == 20

    def test_worker_cfg_creates_node(self):
        """Test that cfg method creates a Node."""
        worker = Worker(func_with_args, data_type=DummyData)
        node = worker.cfg(multiplier=5)

        assert isinstance(node, Node)
        assert node.worker == worker
        assert node.config == {"multiplier": 5}

    def test_worker_cfg_empty_kwargs(self):
        """Test cfg method with empty kwargs."""
        worker = Worker(func_without_args, data_type=DummyData)
        node = worker.cfg()

        assert isinstance(node, Node)
        assert node.config == {}

    def test_worker_repr(self):
        """Test worker string representation."""
        worker = Worker(func_without_args, name="test_worker", data_type=DummyData)
        repr_str = repr(worker)
        assert repr_str == "Worker(name='test_worker', type=DummyData)"

    # TODO: Add test for worker with None data_type
    # TODO: Add test for worker with wrong data_type


if __name__ == "__main__":
    pytest.main([__file__])
