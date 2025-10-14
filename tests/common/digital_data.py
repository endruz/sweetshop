from sweetshop import BaseData


class DigitalData(BaseData):
    """Digital data class for worker testing."""

    def __init__(self, value: float):
        super().__init__()
        self.value = value

    def __repr__(self):
        return f"DigitalData(value={self.value})"

    def __eq__(self, other):
        return isinstance(other, DigitalData) and self.value == other.value


def initial_data() -> DigitalData:
    """Create initial DigitalData with value 0."""
    return DigitalData(0)


def add_one(data: DigitalData) -> DigitalData:
    """Add one to the value."""
    return DigitalData(data.value + 1)


def add_value(data: DigitalData, value: float) -> DigitalData:
    """Add a specific value."""
    return DigitalData(data.value + value)


def multiply_by_two(data: DigitalData) -> DigitalData:
    """Multiply the value by two."""
    return DigitalData(data.value * 2)
