"""SoilProfile value object representing vertically stacked soil layers."""

import math
from dataclasses import dataclass

from backend.domain.constants import MAX_PERCENTAGE, MIN_PERCENTAGE
from backend.domain.exceptions import InvalidProfileError
from backend.domain.value_objects.soil_classification import SoilClassification
from backend.domain.value_objects.soil_layer import SoilLayer


@dataclass(frozen=True, slots=True)
class SoilProfile:
    """Represents a validated, immutable vertical soil profile."""

    layers: tuple[SoilLayer, ...]
    classification: SoilClassification
    composition_share: float | None = None

    def __post_init__(self) -> None:
        """Validate type and layer stack invariants without coercion."""
        # 1. Type validation for layers
        if not isinstance(self.layers, (tuple, list)):
            raise InvalidProfileError(
                "layers must be a tuple or list of SoilLayer instances."
            )

        # Force conversion to tuple
        if not isinstance(self.layers, tuple):
            object.__setattr__(self, "layers", tuple(self.layers))

        # Check element types
        for i, layer in enumerate(self.layers):
            if not isinstance(layer, SoilLayer):
                raise InvalidProfileError(
                    f"All elements in layers must be SoilLayer instances. "
                    f"Element at index {i} is of type '{type(layer).__name__}'."
                )

        # 2. Check at least one layer exists
        if not self.layers:
            raise InvalidProfileError("Profile must contain at least one layer.")

        # 3. Validation for classification
        if not isinstance(self.classification, SoilClassification):
            raise InvalidProfileError(
                "classification must be a SoilClassification instance."
            )

        # 4. Validation for composition_share
        if self.composition_share is not None:
            if (
                not isinstance(self.composition_share, (int, float))
                or isinstance(self.composition_share, bool)
            ):
                raise InvalidProfileError("composition_share must be a numeric value.")

            # Coerce to float
            object.__setattr__(
                self, "composition_share", float(self.composition_share)
            )

            if not math.isfinite(self.composition_share):
                raise InvalidProfileError("composition_share must be a finite number.")

            if (
                self.composition_share < MIN_PERCENTAGE
                or self.composition_share > MAX_PERCENTAGE
            ):
                raise InvalidProfileError(
                    f"composition_share must be between {MIN_PERCENTAGE} "
                    f"and {MAX_PERCENTAGE}. Got {self.composition_share}."
                )

        # 5. Check vertical stacking (order and overlap)
        for i in range(len(self.layers) - 1):
            current_layer = self.layers[i]
            next_layer = self.layers[i + 1]
            if current_layer.bottom_depth_cm > next_layer.top_depth_cm:
                raise InvalidProfileError(
                    f"Layers overlap or are out of order: layer {i} "
                    f"(bottom: {current_layer.bottom_depth_cm} cm) "
                    f"is deeper than layer {i+1} "
                    f"(top: {next_layer.top_depth_cm} cm)."
                )
