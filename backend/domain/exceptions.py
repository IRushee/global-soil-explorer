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


class InvalidLayerError(ValueError):
    """Raised when a SoilLayer violates depth range or property invariants."""
    pass


class InvalidProfileError(ValueError):
    """Raised when a SoilProfile violates layer stack or validation invariants."""
    pass


class InvalidObservationError(ValueError):
    """Raised when a SoilObservation violates domain invariants."""
    pass



