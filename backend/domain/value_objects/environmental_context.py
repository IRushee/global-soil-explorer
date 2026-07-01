"""EnvironmentalContext value object for site climate attributes."""

from dataclasses import dataclass
from typing import Final

from backend.domain.exceptions import InvalidEnvironmentalContextError

VALID_KOPPEN_CLIMATES: Final[frozenset[str]] = frozenset({"A", "B", "C", "D", "E"})


@dataclass(frozen=True, slots=True)
class EnvironmentalContext:
    """Represents environmental, climatic, and topographical context of the soil site.

    Future Placeholders:
    - elevation_m: float | None
    - land_cover_class: str | None
    - terrain_slope_pct: float | None
    - administrative_country_code: str | None
    """

    koppen_climate: str | None = None

    def __post_init__(self) -> None:
        """Validate Koppen-Geiger climate invariants."""
        if self.koppen_climate is not None:
            if not isinstance(self.koppen_climate, str):
                raise InvalidEnvironmentalContextError(
                    "koppen_climate must be a string."
                )
            # Remove any trailing whitespaces (e.g. from raw database fields)
            clean_climate = self.koppen_climate.strip().upper()
            if clean_climate not in VALID_KOPPEN_CLIMATES:
                raise InvalidEnvironmentalContextError(
                    f"Invalid Koppen climate code '{self.koppen_climate}'. "
                    f"Must be one of {sorted(list(VALID_KOPPEN_CLIMATES))}."
                )
            # Override with clean stripped string
            object.__setattr__(self, "koppen_climate", clean_climate)
