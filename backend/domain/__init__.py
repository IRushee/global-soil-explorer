"""Domain package defining core soil science entities and validation rules."""

from backend.domain.exceptions import InvalidCoordinateError
from backend.domain.value_objects.coordinate import Coordinate

__all__ = ["Coordinate", "InvalidCoordinateError"]
