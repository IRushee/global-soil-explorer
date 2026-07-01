"""SoilTexture value object representing USDA and SOTER grain classifications."""

from dataclasses import dataclass
from typing import Final

from backend.domain.exceptions import InvalidSoilTextureError

VALID_USDA_TEXTURES: Final[frozenset[int]] = frozenset(range(1, 14))
VALID_SOTER_TEXTURES: Final[frozenset[str]] = frozenset({"C", "F", "M", "V", "Z"})


@dataclass(frozen=True, slots=True)
class SoilTexture:
    """Represents USDA and SOTER categorical soil texture classes."""

    usda_texture: int | None = None
    soter_texture: str | None = None

    def __post_init__(self) -> None:
        """Validate soil texture invariants."""
        # USDA texture validation
        if self.usda_texture is not None:
            if not isinstance(self.usda_texture, int) or isinstance(
                self.usda_texture, bool
            ):
                raise InvalidSoilTextureError("usda_texture must be an integer.")
            if self.usda_texture not in VALID_USDA_TEXTURES:
                raise InvalidSoilTextureError(
                    f"Invalid usda_texture code '{self.usda_texture}'. "
                    f"Must be one of {sorted(list(VALID_USDA_TEXTURES))}."
                )

        # SOTER texture validation
        if self.soter_texture is not None:
            if not isinstance(self.soter_texture, str):
                raise InvalidSoilTextureError("soter_texture must be a string.")
            clean_soter = self.soter_texture.strip().upper()
            if clean_soter == "-":
                object.__setattr__(self, "soter_texture", None)
            else:
                if clean_soter not in VALID_SOTER_TEXTURES:
                    raise InvalidSoilTextureError(
                        f"Invalid soter_texture code '{self.soter_texture}'. "
                        f"Must be one of {sorted(list(VALID_SOTER_TEXTURES))}."
                    )
                object.__setattr__(self, "soter_texture", clean_soter)
