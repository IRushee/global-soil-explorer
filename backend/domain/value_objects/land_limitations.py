"""LandLimitations value object representing constraints to plant growth."""

from dataclasses import dataclass
from typing import Final

from backend.domain.exceptions import InvalidLandLimitationsError

VALID_ROOT_DEPTHS: Final[frozenset[int]] = frozenset({1, 2, 3, 4})
VALID_ROOT_OBSTACLES: Final[frozenset[int]] = frozenset({0, 1, 2, 3, 4, 5, 6})
VALID_PHASES: Final[frozenset[int]] = frozenset(range(0, 31))
VALID_ADDITIONAL_PROPERTIES: Final[frozenset[int]] = frozenset({0, 1, 2, 3})


def _validate_limit_code(val: int | None, valid_set: frozenset[int], name: str) -> None:
    """Validate numeric code type and dictionary presence."""
    if val is not None:
        if not isinstance(val, int) or isinstance(val, bool):
            raise InvalidLandLimitationsError(f"{name} must be an integer.")
        if val not in valid_set:
            raise InvalidLandLimitationsError(
                f"Invalid {name} code '{val}'. "
                f"Must be one of {sorted(list(valid_set))}."
            )


@dataclass(frozen=True, slots=True)
class LandLimitations:
    """Represents agricultural and physical constraints of the profile."""

    root_depth: int | None = None
    root_obstacles: int | None = None
    phase1: int | None = None
    phase2: int | None = None
    additional_property: int | None = None

    def __post_init__(self) -> None:
        """Validate land limitation invariants."""
        _validate_limit_code(self.root_depth, VALID_ROOT_DEPTHS, "root_depth")
        _validate_limit_code(
            self.root_obstacles, VALID_ROOT_OBSTACLES, "root_obstacles"
        )
        _validate_limit_code(self.phase1, VALID_PHASES, "phase1")
        _validate_limit_code(self.phase2, VALID_PHASES, "phase2")
        _validate_limit_code(
            self.additional_property,
            VALID_ADDITIONAL_PROPERTIES,
            "additional_property",
        )
