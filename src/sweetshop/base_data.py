from abc import ABC
from typing import TypeVar


class BaseData(ABC): ...


TData = TypeVar("TData", bound=BaseData)
