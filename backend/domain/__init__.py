"""Domain package defining core soil science entities and validation rules."""

from backend.domain.exceptions import (
    InvalidClassificationError,
    InvalidCoordinateError,
    InvalidLayerError,
    InvalidPropertyError,
)
from backend.domain.value_objects import (
    Coordinate,
    PropertyType,
    SoilClassification,
    SoilLayer,
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
    "InvalidCoordinateError",
    "InvalidPropertyError",
    "InvalidClassificationError",
    "InvalidLayerError",
]
