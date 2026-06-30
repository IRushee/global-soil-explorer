"""Domain package defining core soil science entities and validation rules."""

from backend.domain.exceptions import (
    InvalidClassificationError,
    InvalidCoordinateError,
    InvalidLayerError,
    InvalidObservationError,
    InvalidProfileError,
    InvalidPropertyError,
)
from backend.domain.value_objects import (
    Coordinate,
    PropertyType,
    SoilClassification,
    SoilLayer,
    SoilObservation,
    SoilProfile,
    SoilProperty,
    Unit,
)

__all__ = [
    "Coordinate",
    "SoilProperty",
    "PropertyType",
    "Unit",
    "SoilClassification",
    "SoilLayer",
    "SoilProfile",
    "SoilObservation",
    "InvalidCoordinateError",
    "InvalidPropertyError",
    "InvalidClassificationError",
    "InvalidLayerError",
    "InvalidProfileError",
    "InvalidObservationError",
]


