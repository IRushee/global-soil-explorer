"""Domain package defining core soil science entities and validation rules."""

from backend.domain.exceptions import (
    InvalidClassificationError,
    InvalidCoordinateError,
    InvalidPropertyError,
)
from backend.domain.value_objects import (
    Coordinate,
    PropertyType,
    SoilClassification,
    SoilProperty,
    Unit,
)

__all__ = [
    "Coordinate",
    "SoilProperty",
    "PropertyType",
    "Unit",
    "SoilClassification",
    "InvalidCoordinateError",
    "InvalidPropertyError",
    "InvalidClassificationError",
]
