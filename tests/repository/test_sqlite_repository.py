"""Integration tests for the SQLiteSoilObservationRepository."""

from pathlib import Path

import pytest
from backend.domain import Coordinate, SoilObservation
from backend.repository.sqlite_repository import (
    SQLiteSoilObservationRepository,
)

DB_PATH = Path("../data/output/hwsd.db")


def test_repository_database_not_found() -> None:
    """Verify that initialization fails if the SQLite database is missing."""
    with pytest.raises(FileNotFoundError):
        SQLiteSoilObservationRepository("nonexistent.db")


def test_repository_invalid_key() -> None:
    """Verify that get_by_key raises KeyError for nonexistent SMU keys."""
    if not DB_PATH.exists():
        pytest.skip("Generated SQLite database not found.")

    repo = SQLiteSoilObservationRepository(DB_PATH)
    with pytest.raises(KeyError):
        repo.get_by_key(9999999)


def test_repository_successful_resolution() -> None:
    """Verify that a valid SMU key returns a fully populated SoilObservation."""
    if not DB_PATH.exists():
        pytest.skip("Generated SQLite database not found.")

    repo = SQLiteSoilObservationRepository(DB_PATH)

    # Use SMU ID 1666 (known to exist)
    coord = Coordinate(12.34, 56.78)
    obs = repo.get_by_key(1666, coordinate=coord)

    assert isinstance(obs, SoilObservation)
    assert obs.coordinate == coord
    assert len(obs.profiles) > 0

    # Inspect the first profile component
    profile = obs.profiles[0]
    assert profile.classification.class_symbol != ""
    assert profile.classification.class_name != ""
    share = profile.composition_share
    assert share is not None
    assert share > 0.0


    # Inspect layers within the profile
    assert len(profile.layers) > 0
    for layer in profile.layers:
        top = layer.top_depth_cm
        bottom = layer.bottom_depth_cm
        assert top is not None
        assert bottom is not None
        assert top <= bottom
        # Verify layer properties are parsed
        for prop in layer.properties:
            assert prop.value is not None
            # Values must be within valid physical bounds
            assert prop.value >= 0.0 or prop.property_type.value == "ph_water"


