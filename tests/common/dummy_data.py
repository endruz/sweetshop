from sweetshop import BaseData


class DummyData(BaseData):
    """Dummy data class for worker testing."""

    def __init__(self, value: int):
        super().__init__()
        self.value = value

    def __repr__(self):
        return f"DummyData(value={self.value})"

    def __eq__(self, other):
        return isinstance(other, DummyData) and self.value == other.value
