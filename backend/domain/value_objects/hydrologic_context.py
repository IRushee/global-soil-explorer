"""HydrologicContext value object representing profile-level water dynamics."""

from dataclasses import dataclass
from typing import Final

from backend.domain.exceptions import InvalidHydrologicContextError

VALID_DRAINAGE_CODES: Final[frozenset[str]] = frozenset(
    {"E", "I", "MW", "P", "SE", "VP", "W"}
)
VALID_WATER_REGIMES: Final[frozenset[int]] = frozenset({0, 1, 2, 3, 4})
VALID_IMPERMEABLE_LAYERS: Final[frozenset[int]] = frozenset({0, 1, 2, 3, 4})


@dataclass(frozen=True, slots=True)
class HydrologicContext:
    """Represents natural drainage ratings, water regimes, and impermeable layers."""

    drainage: str | None = None
    water_regime: int | None = None
    impermeable_layer: int | None = None

    def __post_init__(self) -> None:
        """Validate hydrologic context invariants."""
        # Validate drainage
        if self.drainage is not None:
            if not isinstance(self.drainage, str):
                raise InvalidHydrologicContextError("drainage must be a string.")
            clean_drainage = self.drainage.strip().upper()
            if clean_drainage not in VALID_DRAINAGE_CODES:
                raise InvalidHydrologicContextError(
                    f"Invalid drainage code '{self.drainage}'. "
                    f"Must be one of {sorted(list(VALID_DRAINAGE_CODES))}."
                )
            object.__setattr__(self, "drainage", clean_drainage)

        # Validate water regime
        if self.water_regime is not None:
            if not isinstance(self.water_regime, int) or isinstance(
                self.water_regime, bool
            ):
                raise InvalidHydrologicContextError("water_regime must be an integer.")
            if self.water_regime not in VALID_WATER_REGIMES:
                raise InvalidHydrologicContextError(
                    f"Invalid water_regime code '{self.water_regime}'. "
                    f"Must be one of {sorted(list(VALID_WATER_REGIMES))}."
                )

        # Validate impermeable layer
        if self.impermeable_layer is not None:
            if not isinstance(self.impermeable_layer, int) or isinstance(
                self.impermeable_layer, bool
            ):
                raise InvalidHydrologicContextError(
                    "impermeable_layer must be an integer."
                )
            if self.impermeable_layer not in VALID_IMPERMEABLE_LAYERS:
                raise InvalidHydrologicContextError(
                    f"Invalid impermeable_layer code '{self.impermeable_layer}'. "
                    f"Must be one of {sorted(list(VALID_IMPERMEABLE_LAYERS))}."
                )
