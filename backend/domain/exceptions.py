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


class InvalidEnvironmentalContextError(ValueError):
    """Raised when an EnvironmentalContext violates invariants."""

    pass


class InvalidHydrologicContextError(ValueError):
    """Raised when a HydrologicContext violates invariants."""

    pass


class InvalidLandLimitationsError(ValueError):
    """Raised when LandLimitations violate invariants."""

    pass


class InvalidSoilTextureError(ValueError):
    """Raised when a SoilTexture violates invariants."""

    pass


class InvalidLayerMeasurementsError(ValueError):
    """Raised when LayerMeasurements violate invariants."""

    pass


class InvalidDatasetMetadataError(ValueError):
    """Raised when DatasetMetadata violates invariants."""

    pass
