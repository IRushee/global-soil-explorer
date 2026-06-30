"""Unit tests for the SoilLayer value object."""

from dataclasses import FrozenInstanceError

import pytest
from backend.domain import (
    InvalidLayerError,
    PropertyType,
    SoilLayer,
    SoilProperty,
    Unit,
)


def test_valid_soil_layer() -> None:
    """Verify that a valid SoilLayer is successfully created."""
    p1 = SoilProperty(PropertyType.PH_WATER, 6.5, Unit.PH)
    p2 = SoilProperty(PropertyType.CLAY, 25.0, Unit.PERCENT)

    # With tuple
    layer1 = SoilLayer(0, 30, (p1, p2))
    assert layer1.top_depth_cm == 0.0
    assert layer1.bottom_depth_cm == 30.0
    assert isinstance(layer1.top_depth_cm, float)
    assert isinstance(layer1.bottom_depth_cm, float)
    assert layer1.properties == (p1, p2)

    # With list (coerced to tuple in __post_init__)
    layer2 = SoilLayer(10.5, 50.8, [p1, p2])  # type: ignore[arg-type]
    assert layer2.top_depth_cm == 10.5
    assert layer2.bottom_depth_cm == 50.8
    assert layer2.properties == (p1, p2)

    # Empty properties allowed
    layer3 = SoilLayer(0, 100, ())
    assert layer3.properties == ()


def test_invalid_depth_types() -> None:
    """Verify that invalid types for depths raise InvalidLayerError."""
    with pytest.raises(InvalidLayerError, match="top_depth_cm must be"):
        SoilLayer("0", 30, ())  # type: ignore[arg-type]

    with pytest.raises(InvalidLayerError, match="top_depth_cm must be"):
        SoilLayer(True, 30, ())

    with pytest.raises(InvalidLayerError, match="bottom_depth_cm must be"):
        SoilLayer(0, None, ())  # type: ignore[arg-type]

    with pytest.raises(InvalidLayerError, match="bottom_depth_cm must be"):
        SoilLayer(0, False, ())


def test_non_finite_depths() -> None:
    """Verify that NaN or Inf depths raise InvalidLayerError."""
    with pytest.raises(InvalidLayerError, match="top_depth_cm must be a finite"):
        SoilLayer(float("nan"), 30, ())

    with pytest.raises(InvalidLayerError, match="bottom_depth_cm must be a finite"):
        SoilLayer(0, float("inf"), ())


def test_depth_ranges_boundaries() -> None:
    """Verify that depth range boundary invariants are enforced."""
    # Negative top depth
    with pytest.raises(InvalidLayerError, match="top_depth_cm cannot be negative"):
        SoilLayer(-0.1, 30, ())

    # Non-positive bottom depth
    with pytest.raises(InvalidLayerError, match="bottom_depth_cm must be strictly"):
        SoilLayer(0, 0, ())

    with pytest.raises(InvalidLayerError, match="bottom_depth_cm must be strictly"):
        SoilLayer(0, -5, ())

    # Top depth greater than or equal to bottom depth
    with pytest.raises(InvalidLayerError, match="must be strictly less than"):
        SoilLayer(30, 30, ())

    with pytest.raises(InvalidLayerError, match="must be strictly less than"):
        SoilLayer(40, 30, ())


def test_invalid_property_collection_types() -> None:
    """Verify that invalid property collection types raise InvalidLayerError."""
    with pytest.raises(InvalidLayerError, match="properties must be a tuple"):
        SoilLayer(0, 30, "not a sequence")  # type: ignore[arg-type]

    p_valid = SoilProperty(PropertyType.PH_WATER, 6.5, Unit.PH)
    with pytest.raises(InvalidLayerError, match="All elements in properties"):
        SoilLayer(0, 30, (p_valid, "invalid_element"))  # type: ignore[arg-type]


def test_duplicate_property_types() -> None:
    """Verify that duplicate PropertyTypes within the same layer are rejected."""
    p1 = SoilProperty(PropertyType.PH_WATER, 6.5, Unit.PH)
    p2 = SoilProperty(PropertyType.PH_WATER, 7.0, Unit.PH)

    with pytest.raises(InvalidLayerError, match="Duplicate property type"):
        SoilLayer(0, 30, (p1, p2))


def test_equality() -> None:
    """Verify standard dataclass structural equality."""
    p1 = SoilProperty(PropertyType.PH_WATER, 6.5, Unit.PH)
    p2 = SoilProperty(PropertyType.CLAY, 25.0, Unit.PERCENT)

    layer1 = SoilLayer(0, 30, (p1, p2))
    layer2 = SoilLayer(0, 30, (p1, p2))
    layer3 = SoilLayer(0.1, 30, (p1, p2))
    layer4 = SoilLayer(0, 30, (p1,))

    assert layer1 == layer2
    assert layer1 != layer3
    assert layer1 != layer4


def test_immutability() -> None:
    """Verify that SoilLayer attributes cannot be modified post-creation."""
    layer = SoilLayer(0, 30, ())
    with pytest.raises(FrozenInstanceError):
        layer.top_depth_cm = 5.0  # type: ignore[misc]

    with pytest.raises(FrozenInstanceError):
        layer.bottom_depth_cm = 40.0  # type: ignore[misc]

    with pytest.raises(FrozenInstanceError):
        layer.properties = ()  # type: ignore[misc]


def test_hashability() -> None:
    """Verify SoilLayer is hashable."""
    p = SoilProperty(PropertyType.PH_WATER, 6.5, Unit.PH)
    layer1 = SoilLayer(0, 30, (p,))
    layer2 = SoilLayer(0, 30, (p,))
    layer3 = SoilLayer(30, 60, ())

    layer_set = {layer1, layer2, layer3}
    assert len(layer_set) == 2


def test_slots_verification() -> None:
    """Verify that SoilLayer has slots and no __dict__ representation."""
    layer = SoilLayer(0, 30, ())
    assert not hasattr(layer, "__dict__")
