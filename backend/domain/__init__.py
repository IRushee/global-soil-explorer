"""Domain package defining core soil science entities and validation rules."""

from backend.domain.exceptions import (
    InvalidClassificationError,
    InvalidCoordinateError,
    InvalidLayerError,
    InvalidProfileError,
    InvalidPropertyError,
)
from backend.domain.value_objects import (
    Coordinate,
    PropertyType,
    SoilClassification,
    SoilLayer,
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
    "InvalidCoordinateError",
    "InvalidPropertyError",
    "InvalidClassificationError",
    "InvalidLayerError",
    "InvalidProfileError",
]

