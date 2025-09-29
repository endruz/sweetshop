from base_data import BaseData
from pipe import Pipe, pipe_registry
from worker import worker_registry


class MathData(BaseData):
    def __init__(self, value: float | int):
        self.value = value

    def __repr__(self):
        return f"MathData(value={self.value})"


@worker_registry.register_worker(data_type=MathData)
def add_(data: MathData, b: int) -> MathData:
    return MathData(data.value + b)


@worker_registry.register_worker(data_type=MathData)
def multiply_(data: MathData, b: int) -> MathData:
    return MathData(data.value * b)


@worker_registry.register_worker(data_type=MathData)
def divide_(data: MathData, b: int) -> MathData:
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return MathData(data.value / b)


@worker_registry.register_worker(data_type=MathData)
def add_one(data: MathData) -> MathData:
    return MathData(data.value + 1)


@worker_registry.register_worker(data_type=MathData)
def reduce_one(data: MathData) -> MathData:
    return MathData(data.value - 1)


@pipe_registry.register_pipe()
def example_pipe() -> Pipe:
    pipe = (
        Pipe(data_type=MathData)
        .start_with(worker_registry.add_.cfg(b=5))  # 10 + 5 = 15
        .then(worker_registry.multiply_.cfg(b=2))  # 15 * 2 = 30
        .then(worker_registry.divide_.cfg(b=3))  # 30 / 3 = 10
        .branch()
        .on(lambda d: d.value > 5, worker_registry.add_one.cfg())  # 10 + 1 = 11
        .then(worker_registry.multiply_.cfg(b=2))  # 11 * 2 = 22
        .on(lambda d: d.value < 5, worker_registry.reduce_one.cfg())  # won't execute
        .end_branch()
        .then(worker_registry.reduce_one.cfg())  # 22 - 1 = 21
    )

    return pipe


if __name__ == "__main__":
    pipe = pipe_registry.example_pipe
    data = MathData(10)
    result = pipe.execute(data)
    print(result)  # MathData(value=21)
