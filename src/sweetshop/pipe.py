from collections import deque
from collections.abc import Callable
from typing import Generic, Type

from sweetshop.base_data import TData
from sweetshop.registry import BaseRegistry
from sweetshop.worker import Worker


class Node(Generic[TData]):
    def __init__(self, worker: Worker, config: dict | None = None):
        self.worker: Worker = worker
        self.config: dict = config or {}
        self.next_nodes: list["Node"] = []
        self.condition: Callable | None = None

    def add_next(self, node: "Node", condition: Callable | None = None):
        self.next_nodes.append(node)
        node.condition = condition

    def execute(self, data: TData) -> TData:
        """Execute the node with given data"""
        return self.worker.execute(data, **self.config)

    def __repr__(self):
        return f"Node(worker={self.worker}, config={self.config})"


class Pipe(Generic[TData]):
    def __init__(self, data_type: Type[TData]):
        self.data_type: Type[TData] = data_type
        self.start_node: Node | None = None
        self.current_node: Node | None = None
        # Branch management
        self.branch_node: Node | None = None
        self.branch_end_nodes: list[Node] = []  # Track all branch end nodes

    def start_with(self, node: Node) -> "Pipe":
        self.start_node = node
        self.current_node = node
        return self

    def then(self, node: Node) -> "Pipe":
        """Connect the next node in sequence"""
        if self.current_node is None:
            raise ValueError("No current node to connect to")

        # We're after end_branch() - connect to all branch end nodes
        if not self.branch_node and self.branch_end_nodes:
            for end_node in self.branch_end_nodes:
                end_node.add_next(node)
            self.branch_end_nodes.clear()  # Clear after connecting
        else:
            # Normal sequential connection
            self.current_node.add_next(node)

        self.current_node = node
        return self

    def branch(self) -> "Pipe":
        """Start a branching structure"""
        self.branch_node = self.current_node
        self.branch_end_nodes.clear()
        return self

    def on(self, condition_func: Callable, node: Node) -> "Pipe":
        """Start a conditional branch with given condition function"""
        if self.current_node is None:
            raise ValueError("No current node to connect to")

        if self.branch_node is None:
            raise ValueError("Must call branch() before on()")

        self.branch_node.add_next(node, condition_func)

        # If we have a previous branch chain, record its end node
        if self.current_node != self.branch_node:
            self.branch_end_nodes.append(self.current_node)

        # Set current_node to the new branch node for then() calls
        self.current_node = node
        return self

    def end_branch(self) -> "Pipe":
        """End the current branching structure"""
        if self.current_node is None:
            raise ValueError("No current node to connect to")

        if self.branch_node is None:
            raise ValueError("No active branch to end")

        # Add the current node as a branch end node if it's not the start node
        if self.current_node != self.branch_node:
            self.branch_end_nodes.append(self.current_node)

        # Clear branch state
        self.branch_node = None
        # current_node will be set by the next then() call
        return self

    def execute(self, data: TData) -> TData:
        """Execute the pipe with the given initial data"""
        if self.start_node is None:
            raise ValueError("Pipe has no start node")

        # Use BFS to traverse the pipe
        queue = deque([(self.start_node, data)])
        final_results = []

        while queue:
            current_node, current_data = queue.popleft()

            # Execute current node
            try:
                result_data = current_node.execute(current_data)
            except Exception as e:
                raise RuntimeError(f"Node {current_node} execution failed: {e}")

            # Check if this node has any next nodes
            has_next: bool = False
            for next_node in current_node.next_nodes:
                if next_node.condition is None or next_node.condition(result_data):
                    queue.append((next_node, result_data))
                    has_next = True

            # If no next nodes executed, this could be a final result
            if not has_next:
                final_results.append(result_data)

        # TODO: support multiple final results
        return final_results[0]

    def __repr__(self):
        return f"Pipe(data_type={self.data_type.__name__})"


class PipeRegistry(BaseRegistry[Pipe]):
    """Registry for managing Pipe instances."""

    def __getattr__(self, name: str) -> Pipe:
        """Allow accessing pipes as attributes."""
        if self.exists(name):
            return self._registry[name]
        raise AttributeError(f"Pipe '{name}' not found in registry")

    def register_pipe(self, name: str | None = None) -> Callable:
        """Register decorator for pipes"""

        def wrapper(func: Callable[[], Pipe]) -> None:
            nonlocal name
            name = name or getattr(func, "__name__", "unknown_pipe")
            pipe: Pipe = func()

            self.register(name, pipe)

        return wrapper


# Global pipe registry instance
pipe_registry = PipeRegistry()
