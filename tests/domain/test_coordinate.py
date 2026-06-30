"""Unit tests for the Coordinate value object."""

from dataclasses import FrozenInstanceError

import pytest
from backend.domain import Coordinate, InvalidCoordinateError


def test_valid_coordinates() -> None:
    """Verify that valid coordinates are correctly instantiated."""
    c1 = Coordinate(0.0, 0.0)
    assert c1.latitude == 0.0
    assert c1.longitude == 0.0

    # Integers should be allowed (will be kept as is, but are numeric)
    c2 = Coordinate(10, 20)
    assert c2.latitude == 10
    assert c2.longitude == 20


def test_boundary_values() -> None:
    """Verify that extreme valid boundary coordinates succeed."""
    c_min = Coordinate(-90.0, -180.0)
    assert c_min.latitude == -90.0
    assert c_min.longitude == -180.0

    c_max = Coordinate(90.0, 180.0)
    assert c_max.latitude == 90.0
    assert c_max.longitude == 180.0


def test_invalid_latitude_ranges() -> None:
    """Verify that out-of-bounds latitudes raise InvalidCoordinateError."""
    with pytest.raises(InvalidCoordinateError, match="Latitude must be between"):
        Coordinate(90.1, 0.0)

    with pytest.raises(InvalidCoordinateError, match="Latitude must be between"):
        Coordinate(-90.1, 0.0)


def test_invalid_longitude_ranges() -> None:
    """Verify that out-of-bounds longitudes raise InvalidCoordinateError."""
    with pytest.raises(InvalidCoordinateError, match="Longitude must be between"):
        Coordinate(0.0, 180.1)

    with pytest.raises(InvalidCoordinateError, match="Longitude must be between"):
        Coordinate(0.0, -180.1)


def test_nan_values() -> None:
    """Verify that NaN coordinates raise InvalidCoordinateError."""
    with pytest.raises(InvalidCoordinateError, match="Latitude must be a finite"):
        Coordinate(float("nan"), 0.0)

    with pytest.raises(InvalidCoordinateError, match="Longitude must be a finite"):
        Coordinate(0.0, float("nan"))


def test_infinite_values() -> None:
    """Verify that infinite coordinates raise InvalidCoordinateError."""
    with pytest.raises(InvalidCoordinateError, match="Latitude must be a finite"):
        Coordinate(float("inf"), 0.0)

    with pytest.raises(InvalidCoordinateError, match="Latitude must be a finite"):
        Coordinate(float("-inf"), 0.0)

    with pytest.raises(InvalidCoordinateError, match="Longitude must be a finite"):
        Coordinate(0.0, float("inf"))

    with pytest.raises(InvalidCoordinateError, match="Longitude must be a finite"):
        Coordinate(0.0, float("-inf"))


def test_none_values() -> None:
    """Verify that None values raise InvalidCoordinateError."""
    with pytest.raises(InvalidCoordinateError, match="Latitude must be a numeric"):
        Coordinate(None, 0.0)  # type: ignore

    with pytest.raises(InvalidCoordinateError, match="Longitude must be a numeric"):
        Coordinate(0.0, None)  # type: ignore


def test_strict_types() -> None:
    """Verify that non-numeric types raise InvalidCoordinateError without coercion."""
    # Strings
    with pytest.raises(InvalidCoordinateError, match="Latitude must be a numeric"):
        Coordinate("12.3", 0.0)  # type: ignore

    with pytest.raises(InvalidCoordinateError, match="Longitude must be a numeric"):
        Coordinate(0.0, "45.6")  # type: ignore

    # Booleans (since bool is a subclass of int, strict checking must reject it)
    with pytest.raises(InvalidCoordinateError, match="Latitude must be a numeric"):
        Coordinate(True, 0.0)

    with pytest.raises(InvalidCoordinateError, match="Longitude must be a numeric"):
        Coordinate(0.0, False)


def test_equality() -> None:
    """Verify standard dataclass structural equality."""
    c1 = Coordinate(12.34, 56.78)
    c2 = Coordinate(12.34, 56.78)
    c3 = Coordinate(56.78, 12.34)

    assert c1 == c2
    assert c1 != c3


def test_immutability() -> None:
    """Verify that Coordinate attributes cannot be modified after instantiation."""
    c = Coordinate(10.0, 20.0)

    with pytest.raises(FrozenInstanceError):
        c.latitude = 30.0  # type: ignore

    with pytest.raises(FrozenInstanceError):
        c.longitude = 40.0  # type: ignore


def test_hashability() -> None:
    """Verify Coordinate is hashable and works in sets/dicts."""
    c1 = Coordinate(1.0, 2.0)
    c2 = Coordinate(1.0, 2.0)
    c3 = Coordinate(3.0, 4.0)

    coordinate_set = {c1, c2, c3}
    assert len(coordinate_set) == 2
    assert c1 in coordinate_set
    assert c3 in coordinate_set
