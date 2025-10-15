import pytest

from sweetshop import Pipe, Worker, worker_registry
from tests.common.digital_data import DigitalData, add_one, add_value, multiply_by_two


class TestPipe:
    """Test cases for Pipe class."""

    def setup_method(self):
        """Set up test pipe for each test."""
        worker_registry.register("add_one", Worker(add_one, data_type=DigitalData))
        worker_registry.register("add_value", Worker(add_value, data_type=DigitalData))
        worker_registry.register(
            "multiply_by_two",
            Worker(multiply_by_two, data_type=DigitalData),
        )

    def teardown_method(self):
        """tear down after each test."""
        worker_registry.clear()

    def test_pipe_creation(self):
        """Test creating a new pipe."""
        pipe = Pipe(data_type=DigitalData)

        assert pipe.data_type == DigitalData
        assert pipe.start_node is None
        assert pipe.current_node is None
        assert pipe.branch_node is None
        assert pipe.branch_end_nodes == []

    def test_pipe_start_with(self):
        """Test setting start node."""
        worker = worker_registry.add_one
        node = worker.cfg()
        pipe = Pipe(data_type=DigitalData)

        result_pipe = pipe.start_with(node)

        assert pipe.start_node == node
        assert pipe.current_node == node
        assert result_pipe == pipe

    def test_pipe_then_simple(self):
        """Test simple then connection."""
        node1 = worker_registry.add_one.cfg()
        node2 = worker_registry.add_value.cfg(value=5)

        pipe = Pipe(data_type=DigitalData)
        result_pipe = pipe.start_with(node1).then(node2)

        assert node1.next_nodes == [node2]
        assert pipe.current_node == node2
        assert result_pipe == pipe

    def test_pipe_then_no_current_node(self):
        """Test then with no current node raises error."""
        pipe = Pipe(data_type=DigitalData)

        with pytest.raises(ValueError, match="No current node to connect to"):
            pipe.then(worker_registry.add_one.cfg())

    def test_pipe_execute_simple(self):
        """Test executing simple pipe."""
        pipe = Pipe(data_type=DigitalData)
        pipe.start_with(worker_registry.add_one.cfg()).then(
            worker_registry.add_value.cfg(value=5)
        )

        result = pipe.execute(DigitalData(5))
        assert result == DigitalData(11)  # (5 + 1) + 5 = 11

    def test_pipe_execute_no_start_node(self):
        """Test executing pipe with no start node raises error."""
        pipe = Pipe(data_type=DigitalData)

        with pytest.raises(ValueError, match="Pipe has no start node"):
            pipe.execute(DigitalData(5))

    def test_pipe_execute_with_failure(self):
        """Test executing pipe with failing node."""

        @worker_registry.register_worker(data_type=DigitalData)
        def failing_func():
            raise Exception("Intentional Failure")

        pipe = Pipe(data_type=DigitalData)
        pipe.start_with(worker_registry.add_one.cfg()).then(
            worker_registry.failing_func.cfg()
        )

        with pytest.raises(RuntimeError, match=r"Node .* execution failed"):
            pipe.execute(DigitalData(5))

    def test_pipe_branch_condition_true(self):
        """Test branching when condition is true."""
        pipe = Pipe(data_type=DigitalData)
        (
            pipe.start_with(worker_registry.add_one.cfg())
            .branch()
            .on(lambda d: d.value > 0, worker_registry.multiply_by_two.cfg())
            .end_branch()
            .then(worker_registry.add_value.cfg(value=5))
        )

        result = pipe.execute(DigitalData(5))
        assert result == DigitalData(17)  # (5 + 1) * 2 + 5 = 17

    # TODO: fix this test
    # def test_pipe_branch_condition_false(self):
    #     """Test branching when condition is false."""
    #     pipe = Pipe(data_type=DigitalData)
    #     (
    #         pipe.start_with(worker_registry.add_one.cfg())
    #         .branch()
    #         .on(lambda d: d.value < 0, worker_registry.multiply_by_two.cfg())
    #         .end_branch()
    #         .then(worker_registry.add_value.cfg(value=5))
    #     )

    #     result = pipe.execute(DigitalData(5))
    #     assert result == DigitalData(11)  # (5 + 1) + 5 = 11

    def test_pipe_end_branch_immediately(self):
        """Test ending branch immediately after starting it."""
        pipe = Pipe(data_type=DigitalData)

        (
            pipe.start_with(worker_registry.add_one.cfg())
            .branch()
            .end_branch()
            .then(worker_registry.multiply_by_two.cfg())
        )

        result = pipe.execute(DigitalData(5))
        assert result == DigitalData(12)  # (5 + 1) * 2 = 12

    def test_pipe_branch_multiple_conditions(self):
        """Test branching with multiple conditions."""
        pipe = Pipe(data_type=DigitalData)

        (
            pipe.start_with(worker_registry.add_one.cfg())
            .branch()
            .on(lambda d: d.value > 0, worker_registry.add_value.cfg(value=10))
            .on(lambda d: d.value < 0, worker_registry.add_value.cfg(value=-10))
            .end_branch()
            .then(worker_registry.multiply_by_two.cfg())
        )

        result = pipe.execute(DigitalData(5))
        assert result == DigitalData(32)  # ((5 + 1) + 10) * 2 = 32

    def test_pipe_when_on_without_current_node(self):
        """Test on() without current node raises error."""
        pipe = Pipe(data_type=DigitalData)

        with pytest.raises(ValueError, match="No current node to connect to"):
            pipe.on(lambda d: d.value > 0, worker_registry.add_one.cfg())

    def test_pipe_when_on_without_branch(self):
        """Test on() without branch() raises error."""
        pipe = Pipe(data_type=DigitalData)
        pipe.start_with(worker_registry.add_one.cfg())

        with pytest.raises(ValueError, match=r"Must call branch\(\) before on\(\)"):
            pipe.on(lambda d: d.value > 0, worker_registry.add_one.cfg())

    def test_pipe_end_branch_without_current_node(self):
        """Test end_branch() without current node raises error."""
        pipe = Pipe(data_type=DigitalData)

        with pytest.raises(ValueError, match="No current node to connect to"):
            pipe.end_branch()

    def test_pipe_end_branch_without_branch(self):
        """Test end_branch() without branch() raises error."""
        pipe = Pipe(data_type=DigitalData)
        pipe.start_with(worker_registry.add_one.cfg())

        with pytest.raises(ValueError, match="No active branch to end"):
            pipe.end_branch()

    def test_pipe_repr(self):
        """Test pipe string representation."""
        pipe = Pipe(data_type=DigitalData)
        repr_str = repr(pipe)

        assert repr_str == "Pipe(data_type=DigitalData)"


if __name__ == "__main__":
    pytest.main([__file__])
