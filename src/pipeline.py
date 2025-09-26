import re
from uuid import uuid4
from worker import Worker
from collections.abc import Callable
from collections import deque, OrderedDict


class PipelineNode:
    def __init__(self, worker: Worker, inputs: dict = {}):
        self.id = str(uuid4())
        self.worker: Worker = worker
        self.inputs: dict = inputs
        self.outputs: dict = {}
        self.next_nodes: list["PipelineNode"] = []
        self.condition: Callable | None = None

    def add_next(self, node: "PipelineNode", condition: Callable | None = None):
        self.next_nodes.append(node)
        node.condition = condition

    def execute(self, context: dict) -> dict:
        inputs: dict = {}
        for key, value in self.inputs.items():
            if isinstance(value, str) and re.match(r"^node_[\w-]+_result$", value):
                inputs[key] = context.get(value, value)
            else:
                inputs[key] = value

        result = self.worker.run(**inputs)

        self.outputs = {"result": result}
        context[f"node_{self.id}_result"] = result
        return result

    def __repr__(self):
        return f"PipelineNode(id='{self.id}', worker={self.worker})"


class Pipeline:
    def __init__(self, name: str | None = None):
        self.name = name or "Pipeline"
        self.id = str(uuid4())
        self.start_nodes: list[PipelineNode] = []

    def set_start(self, node: PipelineNode):
        if node not in self.start_nodes:
            self.start_nodes.append(node)

    def connect(
        self,
        from_node: PipelineNode,
        to_node: PipelineNode,
        condition: Callable | None = None,
    ):
        from_node.add_next(to_node, condition)

    def fork(self, from_node: PipelineNode, to_nodes: list[PipelineNode]):
        for to_node in to_nodes:
            from_node.add_next(to_node)

    def merge(self, from_nodes: list[PipelineNode], to_node: PipelineNode):
        for from_node in from_nodes:
            from_node.add_next(to_node)

    def execute(self) -> OrderedDict:
        context: OrderedDict = OrderedDict()

        queue: deque[PipelineNode] = deque(self.start_nodes)

        while queue:
            current_node: PipelineNode = queue.popleft()

            if current_node.condition and not current_node.condition(context):
                continue

            current_node.execute(context)

            for next_node in current_node.next_nodes:
                queue.append(next_node)

        return context

    def __repr__(self):
        return f"Pipeline(name='{self.name}', id='{self.id}')"
