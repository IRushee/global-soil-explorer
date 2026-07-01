"""SoilClassification value object representing taxonomic classifications."""

from dataclasses import dataclass

from backend.domain.exceptions import InvalidClassificationError


@dataclass(frozen=True, slots=True)
class SoilClassification:
    """Represents a validated, immutable taxonomic soil classification."""

    taxonomy_standard: str
    class_symbol: str
    class_name: str
    wrb4_code: str | None = None
    wrb4_name: str | None = None
    wrb2_code: str | None = None
    wrb2_name: str | None = None
    fao90_code: str | None = None
    fao90_name: str | None = None
    wrb_phase_code: str | None = None
    wrb_phase_name: str | None = None
    dominant_group_code: str | None = None
    national_classification: str | None = None

    def __post_init__(self) -> None:
        """Validate type and content invariants without coercion."""
        # 1. Type validation
        if not isinstance(self.taxonomy_standard, str):
            raise InvalidClassificationError("taxonomy_standard must be a string.")
        if not isinstance(self.class_symbol, str):
            raise InvalidClassificationError("class_symbol must be a string.")
        if not isinstance(self.class_name, str):
            raise InvalidClassificationError("class_name must be a string.")

        # 2. Content validation
        if not self.taxonomy_standard.strip():
            raise InvalidClassificationError(
                "taxonomy_standard cannot be empty or whitespace."
            )
        if not self.class_symbol.strip():
            raise InvalidClassificationError(
                "class_symbol cannot be empty or whitespace."
            )
        if not self.class_name.strip():
            raise InvalidClassificationError(
                "class_name cannot be empty or whitespace."
            )

        # 3. Optional taxonomic fields validation
        for field_name in (
            "wrb4_code",
            "wrb4_name",
            "wrb2_code",
            "wrb2_name",
            "fao90_code",
            "fao90_name",
            "wrb_phase_code",
            "wrb_phase_name",
            "dominant_group_code",
            "national_classification",
        ):
            val = getattr(self, field_name)
            if val is not None and not isinstance(val, str):
                raise InvalidClassificationError(f"{field_name} must be a string.")
