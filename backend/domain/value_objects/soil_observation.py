"""SoilObservation value object representing soil observations."""

from dataclasses import dataclass

from backend.domain.exceptions import InvalidObservationError
from backend.domain.value_objects.coordinate import Coordinate
from backend.domain.value_objects.soil_profile import SoilProfile


@dataclass(frozen=True, slots=True)
class SoilObservation:
    """Represents a validated, immutable snapshot of soil observations."""

    coordinate: Coordinate
    profiles: tuple[SoilProfile, ...]

    def __post_init__(self) -> None:
        """Validate type and content invariants without coercion."""
        # 1. Coordinate type validation
        if not isinstance(self.coordinate, Coordinate):
            raise InvalidObservationError(
                "coordinate must be a Coordinate instance."
            )

        # 2. Profiles collection validation
        if not isinstance(self.profiles, (tuple, list)):
            raise InvalidObservationError(
                "profiles must be a tuple or list of SoilProfile instances."
            )

        # Force conversion to tuple
        if not isinstance(self.profiles, tuple):
            object.__setattr__(self, "profiles", tuple(self.profiles))

        # Check element types
        for i, profile in enumerate(self.profiles):
            if not isinstance(profile, SoilProfile):
                raise InvalidObservationError(
                    f"All elements in profiles must be SoilProfile instances. "
                    f"Element at index {i} is of type '{type(profile).__name__}'."
                )

        # 3. Check at least one profile exists
        if not self.profiles:
            raise InvalidObservationError(
                "An observation must contain at least one SoilProfile."
            )

        # 4. Check for duplicate object references
        seen_refs = set()
        for i, profile in enumerate(self.profiles):
            ref_id = id(profile)
            if ref_id in seen_refs:
                raise InvalidObservationError(
                    f"Duplicate profile reference detected at index {i}."
                )
            seen_refs.add(ref_id)
