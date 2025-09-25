from worker import Worker
from pipeline import Pipeline


@Worker.create(name="custom_add")
def custom_add(a: int, b: int) -> int:
    return a + b


@Worker.create(name="custom_multiply")
def custom_multiply(a: int, b: int) -> int:
    return a * b


@Worker.create(name="custom_divide")
def custom_divide(a: int, b: int) -> float:
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


def create_math_pipeline() -> Pipeline:
    p: Pipeline = Pipeline("math_operations")

    # TODO: optimize add_worker
    add_node = p.add_worker(custom_add)
    multiply_node = p.add_worker(custom_multiply)
    divide_node = p.add_worker(custom_divide)
    true_node = p.add_worker(Worker(lambda x: x + 1, "true_node"))
    false_node = p.add_worker(Worker(lambda x: x - 1, "false_node"))

    add_node.inputs = {"a": 10, "b": 5}
    multiply_node.inputs = {"a": "node_" + add_node.id + "_result", "b": 2}
    divide_node.inputs = {"a": "node_" + multiply_node.id + "_result", "b": 3}
    true_node.inputs = {"x": "node_" + divide_node.id + "_result"}
    false_node.inputs = {"x": "node_" + divide_node.id + "_result"}

    p.set_start(add_node)  # 10 + 5 = 15
    p.connect(add_node, multiply_node)  # 15 * 2 = 30
    p.connect(multiply_node, divide_node)  # 30 / 3 = 10
    p.connect(
        divide_node,
        true_node,
        lambda context: context["node_" + divide_node.id + "_result"] == 10,
    )  # 10 + 1 = 11 √
    p.connect(
        divide_node,
        false_node,
        lambda context: context["node_" + divide_node.id + "_result"] != 10,
    )  # 10 - 1 = 9 ×

    return p


if __name__ == "__main__":
    from pprint import pprint

    math_pipeline: Pipeline = create_math_pipeline()
    context = math_pipeline.execute()
    pprint(context)
