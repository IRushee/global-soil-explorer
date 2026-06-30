"""Unit tests for the SoilProperty value object."""

import pytest
from dataclasses import FrozenInstanceError
from types import MappingProxyType

from backend.domain import (
    InvalidPropertyError,
    PropertyType,
    SoilProperty,
    Unit,
)
from backend.domain.value_objects.soil_property import PROPERTY_DEFINITIONS


def test_valid_soil_properties() -> None:
    """Verify that valid properties are successfully instantiated."""
    p1 = SoilProperty(PropertyType.PH_WATER, 6.5, Unit.PH)
    assert p1.property_type == PropertyType.PH_WATER
    assert p1.value == 6.5
    assert p1.unit == Unit.PH

    # Integers must be converted to float
    p2 = SoilProperty(PropertyType.CLAY, 24, Unit.PERCENT)
    assert p2.property_type == PropertyType.CLAY
    assert isinstance(p2.value, float)
    assert p2.value == 24.0
    assert p2.unit == Unit.PERCENT


def test_invalid_types() -> None:
    """Verify that invalid types raise InvalidPropertyError."""
    # Invalid property_type
    with pytest.raises(InvalidPropertyError, match="property_type must be"):
        SoilProperty("ph_water", 6.5, Unit.PH)  # type: ignore

    # Invalid unit
    with pytest.raises(InvalidPropertyError, match="unit must be"):
        SoilProperty(PropertyType.PH_WATER, 6.5, "ph")  # type: ignore

    # Invalid value type (string)
    with pytest.raises(InvalidPropertyError, match="value must be"):
        SoilProperty(PropertyType.PH_WATER, "6.5", Unit.PH)  # type: ignore

    # Invalid value type (bool)
    with pytest.raises(InvalidPropertyError, match="value must be"):
        SoilProperty(PropertyType.PH_WATER, True, Unit.PH)  # type: ignore


def test_invalid_units() -> None:
    """Verify that incorrect units for a property type are rejected with details."""
    with pytest.raises(
        InvalidPropertyError,
        match="Invalid unit for property 'ph_water'. Expected 'ph', got 'percent'",
    ):
        SoilProperty(PropertyType.PH_WATER, 6.5, Unit.PERCENT)


def test_non_finite_values() -> None:
    """Verify that non-finite values are rejected."""
    with pytest.raises(InvalidPropertyError, match="value must be a finite"):
        SoilProperty(PropertyType.PH_WATER, float("nan"), Unit.PH)

    with pytest.raises(InvalidPropertyError, match="value must be a finite"):
        SoilProperty(PropertyType.PH_WATER, float("inf"), Unit.PH)


def test_boundary_validation() -> None:
    """Verify that boundary validations are correctly enforced."""
    # pH water (0.0 to 14.0)
    assert SoilProperty(PropertyType.PH_WATER, 0.0, Unit.PH).value == 0.0
    assert SoilProperty(PropertyType.PH_WATER, 14.0, Unit.PH).value == 14.0
    with pytest.raises(InvalidPropertyError, match="cannot be less than 0.0"):
        SoilProperty(PropertyType.PH_WATER, -0.1, Unit.PH)
    with pytest.raises(InvalidPropertyError, match="cannot be greater than 14.0"):
        SoilProperty(PropertyType.PH_WATER, 14.1, Unit.PH)

    # Clay percentage (0.0 to 100.0)
    assert SoilProperty(PropertyType.CLAY, 0.0, Unit.PERCENT).value == 0.0
    assert SoilProperty(PropertyType.CLAY, 100.0, Unit.PERCENT).value == 100.0
    with pytest.raises(InvalidPropertyError, match="cannot be less than 0.0"):
        SoilProperty(PropertyType.CLAY, -0.1, Unit.PERCENT)
    with pytest.raises(InvalidPropertyError, match="cannot be greater than 100.0"):
        SoilProperty(PropertyType.CLAY, 100.1, Unit.PERCENT)

    # Bulk density (strictly positive)
    bd_property = SoilProperty(
        PropertyType.BULK_DENSITY, 0.01, Unit.GRAM_PER_CUBIC_CENTIMETER
    )
    assert bd_property.value == 0.01
    with pytest.raises(InvalidPropertyError, match="must be strictly positive"):
        SoilProperty(PropertyType.BULK_DENSITY, 0.0, Unit.GRAM_PER_CUBIC_CENTIMETER)
    with pytest.raises(InvalidPropertyError, match="must be strictly positive"):
        SoilProperty(PropertyType.BULK_DENSITY, -0.5, Unit.GRAM_PER_CUBIC_CENTIMETER)

    # Organic carbon (non-negative)
    assert SoilProperty(PropertyType.ORGANIC_CARBON, 0.0, Unit.PERCENT).value == 0.0
    with pytest.raises(InvalidPropertyError, match="cannot be less than 0.0"):
        SoilProperty(PropertyType.ORGANIC_CARBON, -0.01, Unit.PERCENT)


def test_registry_coverage() -> None:
    """Verify that every PropertyType has exactly one definition mapped."""
    assert len(PROPERTY_DEFINITIONS) == len(PropertyType)
    for p_type in PropertyType:
        assert p_type in PROPERTY_DEFINITIONS
        definition = PROPERTY_DEFINITIONS[p_type]
        assert definition.canonical_unit is not None
        assert isinstance(definition.canonical_unit, Unit)


def test_registry_immutability() -> None:
    """Verify that PROPERTY_DEFINITIONS is immutable."""
    assert isinstance(PROPERTY_DEFINITIONS, MappingProxyType)
    with pytest.raises(TypeError):
        PROPERTY_DEFINITIONS[PropertyType.PH_WATER] = None  # type: ignore


def test_enum_uniqueness() -> None:
    """Verify that enum string values are unique."""
    prop_values = [e.value for e in PropertyType]
    unit_values = [e.value for e in Unit]

    assert len(set(prop_values)) == len(prop_values)
    assert len(set(unit_values)) == len(unit_values)

    # Test str subclassing
    assert PropertyType.PH_WATER == "ph_water"
    assert Unit.PERCENT == "percent"


def test_equality() -> None:
    """Verify standard dataclass structural equality."""
    p1 = SoilProperty(PropertyType.CLAY, 25.0, Unit.PERCENT)
    p2 = SoilProperty(PropertyType.CLAY, 25.0, Unit.PERCENT)
    p3 = SoilProperty(PropertyType.CLAY, 20.0, Unit.PERCENT)
    p4 = SoilProperty(PropertyType.SAND, 25.0, Unit.PERCENT)

    assert p1 == p2
    assert p1 != p3
    assert p1 != p4


def test_immutability() -> None:
    """Verify that SoilProperty attributes cannot be modified."""
    p = SoilProperty(PropertyType.PH_WATER, 6.0, Unit.PH)
    with pytest.raises(FrozenInstanceError):
        p.value = 7.0  # type: ignore


def test_hashability() -> None:
    """Verify SoilProperty is hashable."""
    p1 = SoilProperty(PropertyType.CLAY, 25.0, Unit.PERCENT)
    p2 = SoilProperty(PropertyType.CLAY, 25.0, Unit.PERCENT)
    p3 = SoilProperty(PropertyType.SAND, 50.0, Unit.PERCENT)

    prop_set = {p1, p2, p3}
    assert len(prop_set) == 2


def test_slots_verification() -> None:
    """Verify that SoilProperty has slots and no __dict__ representation."""
    p = SoilProperty(PropertyType.PH_WATER, 6.0, Unit.PH)
    assert not hasattr(p, "__dict__")
