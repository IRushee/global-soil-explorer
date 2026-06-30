"""Unit tests for the SoilClassification value object."""

from dataclasses import FrozenInstanceError

import pytest
from backend.domain import InvalidClassificationError, SoilClassification


def test_valid_soil_classification() -> None:
    """Verify that a valid SoilClassification is successfully created."""
    c = SoilClassification("WRB 2022", "ALfr", "Luvic Albeluvisol")
    assert c.taxonomy_standard == "WRB 2022"
    assert c.class_symbol == "ALfr"
    assert c.class_name == "Luvic Albeluvisol"


def test_invalid_types() -> None:
    """Verify that non-string types raise InvalidClassificationError."""
    # taxonomy_standard not a string
    with pytest.raises(InvalidClassificationError, match="taxonomy_standard must be"):
        SoilClassification(123, "ALfr", "Luvic Albeluvisol")  # type: ignore

    # class_symbol not a string
    with pytest.raises(InvalidClassificationError, match="class_symbol must be"):
        SoilClassification("WRB 2022", None, "Luvic Albeluvisol")  # type: ignore

    # class_name not a string
    with pytest.raises(InvalidClassificationError, match="class_name must be"):
        SoilClassification("WRB 2022", "ALfr", True)  # type: ignore


def test_empty_or_whitespace_strings() -> None:
    """Verify that empty or whitespace strings are rejected."""
    # Empty taxonomy_standard
    with pytest.raises(InvalidClassificationError, match="taxonomy_standard cannot be"):
        SoilClassification("", "ALfr", "Luvic Albeluvisol")

    # Whitespace-only class_symbol
    with pytest.raises(InvalidClassificationError, match="class_symbol cannot be"):
        SoilClassification("WRB 2022", "   ", "Luvic Albeluvisol")

    # Whitespace-only class_name
    with pytest.raises(InvalidClassificationError, match="class_name cannot be"):
        SoilClassification("WRB 2022", "ALfr", "\n\t")


def test_equality() -> None:
    """Verify standard dataclass structural equality."""
    c1 = SoilClassification("WRB 2022", "ALfr", "Luvic Albeluvisol")
    c2 = SoilClassification("WRB 2022", "ALfr", "Luvic Albeluvisol")
    c3 = SoilClassification("FAO 1990", "ALfr", "Luvic Albeluvisol")
    c4 = SoilClassification("WRB 2022", "RG", "Regosol")

    assert c1 == c2
    assert c1 != c3
    assert c1 != c4


def test_immutability() -> None:
    """Verify that SoilClassification attributes cannot be modified."""
    c = SoilClassification("WRB 2022", "ALfr", "Luvic Albeluvisol")
    with pytest.raises(FrozenInstanceError):
        c.taxonomy_standard = "FAO 1990"  # type: ignore

    with pytest.raises(FrozenInstanceError):
        c.class_symbol = "RG"  # type: ignore


def test_hashability() -> None:
    """Verify SoilClassification is hashable and works in sets/dicts."""
    c1 = SoilClassification("WRB 2022", "ALfr", "Luvic Albeluvisol")
    c2 = SoilClassification("WRB 2022", "ALfr", "Luvic Albeluvisol")
    c3 = SoilClassification("FAO 1990", "RG", "Regosol")

    class_set = {c1, c2, c3}
    assert len(class_set) == 2
    assert c1 in class_set
    assert c3 in class_set


def test_slots_verification() -> None:
    """Verify that SoilClassification has slots and no __dict__ representation."""
    c = SoilClassification("WRB 2022", "ALfr", "Luvic Albeluvisol")
    assert not hasattr(c, "__dict__")
