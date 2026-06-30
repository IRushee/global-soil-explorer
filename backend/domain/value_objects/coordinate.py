"""Coordinate value object representing a geographic location."""

import math
from dataclasses import dataclass

from backend.domain.exceptions import InvalidCoordinateError

MIN_LATITUDE = -90.0
MAX_LATITUDE = 90.0
MIN_LONGITUDE = -180.0
MAX_LONGITUDE = 180.0


@dataclass(frozen=True)
class Coordinate:
    """Represents a validated immutable geographic coordinate."""

    latitude: float
    longitude: float

    def __post_init__(self) -> None:
        """Validate range and type invariants without coercion."""
        # 1. Type validation (reject boolean subclasses of int)
        if (
            not isinstance(self.latitude, (int, float))
            or isinstance(self.latitude, bool)
        ):
            raise InvalidCoordinateError("Latitude must be a numeric value.")

        if (
            not isinstance(self.longitude, (int, float))
            or isinstance(self.longitude, bool)
        ):
            raise InvalidCoordinateError("Longitude must be a numeric value.")

        # 2. Reject non-finite values (NaN / Inf)
        if not math.isfinite(self.latitude):
            raise InvalidCoordinateError("Latitude must be a finite number.")
        if not math.isfinite(self.longitude):
            raise InvalidCoordinateError("Longitude must be a finite number.")

        # 3. Range validation
        if not (MIN_LATITUDE <= self.latitude <= MAX_LATITUDE):
            raise InvalidCoordinateError(
                f"Latitude must be between {MIN_LATITUDE} "
                f"and {MAX_LATITUDE} degrees. Got {self.latitude}."
            )
        if not (MIN_LONGITUDE <= self.longitude <= MAX_LONGITUDE):
            raise InvalidCoordinateError(
                f"Longitude must be between {MIN_LONGITUDE} "
                f"and {MAX_LONGITUDE} degrees. Got {self.longitude}."
            )
