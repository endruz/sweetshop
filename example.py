from pipeline import Pipeline, PipelineNode
from worker import worker_registry


@worker_registry.register_worker()
def add_(a: int, b: int) -> int:
    return a + b


@worker_registry.register_worker()
def multiply_(a: int, b: int) -> int:
    return a * b


@worker_registry.register_worker()
def divide_(a: int, b: int) -> float:
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


@worker_registry.register_worker()
def add_one(x: float) -> float:
    return x + 1


@worker_registry.register_worker()
def reduce_one(x: float) -> float:
    return x - 1


def create_pipeline() -> Pipeline:
    p: Pipeline = Pipeline()

    add_node = PipelineNode(
        worker_registry.add_,
        inputs={"a": 10, "b": 5},
    )
    multiply_node = PipelineNode(
        worker_registry.multiply_,
        inputs={"a": f"node_{add_node.id}_result", "b": 2},
    )
    divide_node = PipelineNode(
        worker_registry.divide_,
        inputs={"a": f"node_{multiply_node.id}_result", "b": 3},
    )
    true_node = PipelineNode(
        worker_registry.add_one,
        inputs={"x": f"node_{divide_node.id}_result"},
    )
    false_node = PipelineNode(
        worker_registry.reduce_one,
        inputs={"x": f"node_{divide_node.id}_result"},
    )

    p.set_start(add_node)  # 10 + 5 = 15
    p.connect(add_node, multiply_node)  # 15 * 2 = 30
    p.connect(multiply_node, divide_node)  # 30 / 3 = 10
    p.connect(
        divide_node,
        true_node,
        lambda context: context[f"node_{divide_node.id}_result"] == 10,
    )  # 10 + 1 = 11
    p.connect(
        divide_node,
        false_node,
        lambda context: context[f"node_{divide_node.id}_result"] != 10,
    )  # 10 - 1 = 9  won't happen

    return p


if __name__ == "__main__":
    from pprint import pprint

    pipeline: Pipeline = create_pipeline()
    context = pipeline.execute()
    pprint(context)
