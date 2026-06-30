"""SoilLayer value object representing physical and chemical properties at depth."""

import math
from dataclasses import dataclass

from backend.domain.exceptions import InvalidLayerError
from backend.domain.value_objects.soil_property import PropertyType, SoilProperty


@dataclass(frozen=True, slots=True)
class SoilLayer:
    """Represents a validated, immutable vertical soil layer depth interval."""

    top_depth_cm: float
    bottom_depth_cm: float
    properties: tuple[SoilProperty, ...]

    def __post_init__(self) -> None:
        """Validate type and content invariants without coercion."""
        # 1. Type validation for depths
        if (
            not isinstance(self.top_depth_cm, (int, float))
            or isinstance(self.top_depth_cm, bool)
        ):
            raise InvalidLayerError("top_depth_cm must be a numeric value.")

        if (
            not isinstance(self.bottom_depth_cm, (int, float))
            or isinstance(self.bottom_depth_cm, bool)
        ):
            raise InvalidLayerError("bottom_depth_cm must be a numeric value.")

        # Coerce to float
        object.__setattr__(self, "top_depth_cm", float(self.top_depth_cm))
        object.__setattr__(self, "bottom_depth_cm", float(self.bottom_depth_cm))

        # Check finite values
        if not math.isfinite(self.top_depth_cm):
            raise InvalidLayerError("top_depth_cm must be a finite number.")
        if not math.isfinite(self.bottom_depth_cm):
            raise InvalidLayerError("bottom_depth_cm must be a finite number.")

        # 2. Depth range validation
        if self.top_depth_cm < 0.0:
            raise InvalidLayerError(
                f"top_depth_cm cannot be negative. Got {self.top_depth_cm}."
            )
        if self.bottom_depth_cm <= 0.0:
            raise InvalidLayerError(
                "bottom_depth_cm must be strictly positive. "
                f"Got {self.bottom_depth_cm}."
            )
        if self.top_depth_cm >= self.bottom_depth_cm:
            raise InvalidLayerError(
                f"top_depth_cm ({self.top_depth_cm}) must be strictly less than "
                f"bottom_depth_cm ({self.bottom_depth_cm})."
            )

        # 3. Properties collection validation
        if not isinstance(self.properties, (tuple, list)):
            raise InvalidLayerError(
                "properties must be a tuple or list of SoilProperty instances."
            )

        # Force conversion to tuple
        if not isinstance(self.properties, tuple):
            object.__setattr__(self, "properties", tuple(self.properties))

        # Check types of properties and duplicate PropertyTypes
        seen_types: set[PropertyType] = set()
        for p in self.properties:
            if not isinstance(p, SoilProperty):
                raise InvalidLayerError(
                    "All elements in properties must be SoilProperty instances."
                )
            if p.property_type in seen_types:
                raise InvalidLayerError(
                    f"Duplicate property type '{p.property_type.value}' "
                    "detected in layer."
                )
            seen_types.add(p.property_type)
