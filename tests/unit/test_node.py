import pytest

from sweetshop import Node, Worker
from tests.common.digital_data import DigitalData, add_one, add_value, initial_data


class TestNode:
    """Test cases for Node class."""

    def test_node_creation(self):
        """Test creating a new node."""
        worker = Worker(add_one, data_type=DigitalData)
        node = Node(worker)

        assert node.worker == worker
        assert node.config == {}
        assert node.next_nodes == []
        assert node.condition is None

    def test_node_creation_with_config(self):
        """Test creating node with configuration."""
        worker = Worker(add_value, data_type=DigitalData)
        config = {"value": 5}
        node = Node(worker, config)

        assert node.worker == worker
        assert node.config == {"value": 5}
        assert node.next_nodes == []
        assert node.condition is None

    def test_node_add_next(self):
        """Test adding next node."""
        worker1 = Worker(initial_data, data_type=DigitalData)
        worker2 = Worker(add_one, data_type=DigitalData)
        node1 = Node(worker1)
        node2 = Node(worker2)

        node1.add_next(node2)

        assert node1.next_nodes == [node2]
        assert node2.condition is None

    def test_node_add_next_with_condition(self):
        """Test adding next node with condition."""
        worker1 = Worker(initial_data, data_type=DigitalData)
        worker2 = Worker(add_one, data_type=DigitalData)
        node1 = Node(worker1)
        node2 = Node(worker2)

        def condition(x):
            return x.value > 5

        node1.add_next(node2, condition)

        assert node1.next_nodes == [node2]
        assert node2.condition == condition

    def test_node_execute(self):
        """Test node execution."""
        worker = Worker(add_one, data_type=DigitalData)
        node = Node(worker)
        data = DigitalData(5)

        result = node.execute(data)
        assert result == DigitalData(6)

    def test_node_execute_with_config(self):
        """Test node execution with configuration."""
        worker = Worker(add_value, data_type=DigitalData)
        node = Node(worker, {"value": 7})
        data = DigitalData(3)

        result = node.execute(data)
        assert result == DigitalData(10)

    def test_node_repr(self):
        """Test node string representation."""
        worker = Worker(add_one, data_type=DigitalData, name="test_worker")
        node = Node(worker)
        repr_str = repr(node)
        expected_repr: str = (
            r"Node(worker=Worker(name='test_worker', type=DigitalData), config={})"
        )
        assert repr_str == expected_repr


if __name__ == "__main__":
    pytest.main([__file__])
