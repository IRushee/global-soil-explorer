"""Domain exception classes for the Global Soil Explorer."""


class InvalidCoordinateError(ValueError):
    """Raised when a coordinate violates geographic or type invariants."""
    pass


class InvalidPropertyError(ValueError):
    """Raised when a SoilProperty violates type, unit, or range invariants."""
    pass


class InvalidClassificationError(ValueError):
    """Raised when a SoilClassification violates type or validation invariants."""
    pass
