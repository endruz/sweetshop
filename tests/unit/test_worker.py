import pytest

from sweetshop import Node, Worker
from tests.common.digital_data import DigitalData, add_one, add_value, initial_data


class TestWorker:
    """Test cases for Worker class."""

    def test_worker_creation_with_defaults(self):
        """Test creating worker with default name."""
        worker = Worker(initial_data, data_type=DigitalData)
        assert worker.name == "initial_data"
        assert worker.func == initial_data
        assert worker.data_type == DigitalData

    def test_worker_creation_with_custom_name(self):
        """Test creating worker with custom name."""
        worker = Worker(initial_data, name="custom_name", data_type=DigitalData)
        assert worker.name == "custom_name"
        assert worker.func == initial_data
        assert worker.data_type == DigitalData

    def test_worker_creation_with_lambda(self):
        """Test creating worker with lambda function."""

        lambda_func = lambda: DigitalData(99)  # noqa: E731

        worker = Worker(lambda_func, name="lambda_worker", data_type=DigitalData)
        assert worker.name == "lambda_worker"
        assert worker.func == lambda_func

    def test_worker_execute_no_args(self):
        """Test executing worker with no arguments."""
        worker = Worker(initial_data, data_type=DigitalData)

        with pytest.raises(
            TypeError, match="Expected first argument of type DigitalData, got None"
        ):
            worker.execute()

    def test_worker_execute_without_data(self):
        """Test executing worker without data argument."""
        worker = Worker(add_one, data_type=DigitalData)

        with pytest.raises(
            TypeError, match="Expected first argument of type DigitalData, got None"
        ):
            worker.execute(value=10)

    def test_worker_execute_with_only_kwargs(self):
        """Test executing worker with only keyword arguments."""
        worker = Worker(add_one, data_type=DigitalData)
        data = DigitalData(10)

        with pytest.raises(
            TypeError, match="Expected first argument of type DigitalData, got None"
        ):
            worker.execute(data=data)

    def test_worker_execute_with_args(self):
        """Test executing worker with arguments."""
        worker = Worker(add_one, data_type=DigitalData)
        data = DigitalData(10)
        result = worker.execute(data)
        assert isinstance(result, DigitalData)
        assert result.value == 11

    def test_worker_execute_with_kwargs(self):
        """Test executing worker with keyword arguments."""
        worker = Worker(add_value, data_type=DigitalData)
        data = DigitalData(5)
        result = worker.execute(data, value=4)
        assert result.value == 9

    def test_worker_cfg_creates_node(self):
        """Test that cfg method creates a Node."""
        worker = Worker(add_value, data_type=DigitalData)
        node = worker.cfg(value=5)

        assert isinstance(node, Node)
        assert node.worker == worker
        assert node.config == {"value": 5}

    def test_worker_cfg_creates_node_without_args(self):
        """Test that cfg method creates a Node with no config."""
        worker = Worker(add_value, data_type=DigitalData)
        node = worker.cfg()

        assert isinstance(node, Node)
        assert node.worker == worker
        assert node.config == {}

    def test_worker_repr(self):
        """Test worker string representation."""
        worker = Worker(initial_data, name="test_worker", data_type=DigitalData)
        repr_str = repr(worker)
        assert repr_str == "Worker(name='test_worker', type=DigitalData)"

    # TODO: Add test for worker with None data_type
    # TODO: Add test for worker with wrong data_type


if __name__ == "__main__":
    pytest.main([__file__])
