"""Unit tests for the SoilObservation value object."""

from dataclasses import FrozenInstanceError

import pytest
from backend.domain import (
    Coordinate,
    InvalidObservationError,
    PropertyType,
    SoilClassification,
    SoilLayer,
    SoilObservation,
    SoilProfile,
    SoilProperty,
    Unit,
)


@pytest.fixture
def sample_coordinate() -> Coordinate:
    """Fixture for a standard Coordinate."""
    return Coordinate(45.0, 90.0)


@pytest.fixture
def sample_profile() -> SoilProfile:
    """Fixture for a standard SoilProfile."""
    c = SoilClassification("WRB 2022", "ALfr", "Luvic Albeluvisol")
    p = SoilProperty(PropertyType.PH_WATER, 6.5, Unit.PH)
    l1 = SoilLayer(0.0, 30.0, (p,))
    return SoilProfile(layers=(l1,), classification=c)


def test_valid_observation(
    sample_coordinate: Coordinate, sample_profile: SoilProfile
) -> None:
    """Verify that a valid SoilObservation is successfully created."""
    obs = SoilObservation(
        coordinate=sample_coordinate,
        profiles=(sample_profile,),
    )
    assert obs.coordinate == sample_coordinate
    assert obs.profiles == (sample_profile,)


def test_single_profile(
    sample_coordinate: Coordinate, sample_profile: SoilProfile
) -> None:
    """Verify that an observation with a single profile is valid."""
    obs = SoilObservation(coordinate=sample_coordinate, profiles=(sample_profile,))
    assert len(obs.profiles) == 1
    assert obs.profiles[0] == sample_profile


def test_multiple_profiles(
    sample_coordinate: Coordinate, sample_profile: SoilProfile
) -> None:
    """Verify that an observation with multiple profiles is valid."""
    c2 = SoilClassification("WRB 2022", "RG", "Regosol")
    p = SoilProperty(PropertyType.PH_WATER, 6.5, Unit.PH)
    l1 = SoilLayer(0.0, 30.0, (p,))
    profile2 = SoilProfile(layers=(l1,), classification=c2)

    obs = SoilObservation(
        coordinate=sample_coordinate,
        profiles=[sample_profile, profile2],  # type: ignore[arg-type]
    )
    assert isinstance(obs.profiles, tuple)
    assert obs.profiles == (sample_profile, profile2)


def test_invalid_coordinate_type(sample_profile: SoilProfile) -> None:
    """Verify that invalid coordinate types raise InvalidObservationError."""
    with pytest.raises(
        InvalidObservationError, match="coordinate must be a Coordinate"
    ):
        SoilObservation(coordinate="not a coordinate", profiles=(sample_profile,))  # type: ignore[arg-type]


def test_invalid_profile_collection_type(sample_coordinate: Coordinate) -> None:
    """Verify that invalid profile collection types raise InvalidObservationError."""
    with pytest.raises(
        InvalidObservationError, match="profiles must be a tuple or list"
    ):
        SoilObservation(coordinate=sample_coordinate, profiles="not a sequence")  # type: ignore[arg-type]


def test_invalid_profile_elements(
    sample_coordinate: Coordinate, sample_profile: SoilProfile
) -> None:
    """Verify that non-SoilProfile elements raise InvalidObservationError."""
    with pytest.raises(
        InvalidObservationError, match="All elements in profiles must be SoilProfile"
    ):
        SoilObservation(
            coordinate=sample_coordinate,
            profiles=(sample_profile, "not a profile"),  # type: ignore[arg-type]
        )


def test_empty_profile_collection(sample_coordinate: Coordinate) -> None:
    """Verify that an empty profiles collection raises InvalidObservationError."""
    with pytest.raises(
        InvalidObservationError, match="must contain at least one SoilProfile"
    ):
        SoilObservation(coordinate=sample_coordinate, profiles=())


def test_duplicate_profile_references(
    sample_coordinate: Coordinate, sample_profile: SoilProfile
) -> None:
    """Verify that duplicate object references raise InvalidObservationError."""
    with pytest.raises(
        InvalidObservationError, match="Duplicate profile reference detected"
    ):
        SoilObservation(
            coordinate=sample_coordinate,
            profiles=(sample_profile, sample_profile),
        )


def test_immutability(
    sample_coordinate: Coordinate, sample_profile: SoilProfile
) -> None:
    """Verify that SoilObservation attributes cannot be modified post-creation."""
    obs = SoilObservation(coordinate=sample_coordinate, profiles=(sample_profile,))
    with pytest.raises(FrozenInstanceError):
        obs.coordinate = Coordinate(0, 0)  # type: ignore[misc]

    with pytest.raises(FrozenInstanceError):
        obs.profiles = ()  # type: ignore[misc]


def test_equality(sample_coordinate: Coordinate, sample_profile: SoilProfile) -> None:
    """Verify standard dataclass structural equality."""
    obs1 = SoilObservation(coordinate=sample_coordinate, profiles=(sample_profile,))
    obs2 = SoilObservation(coordinate=sample_coordinate, profiles=(sample_profile,))

    c2 = Coordinate(0, 0)
    obs3 = SoilObservation(coordinate=c2, profiles=(sample_profile,))

    assert obs1 == obs2
    assert obs1 != obs3


def test_hashability(
    sample_coordinate: Coordinate, sample_profile: SoilProfile
) -> None:
    """Verify SoilObservation is hashable and works in sets/dicts."""
    obs1 = SoilObservation(coordinate=sample_coordinate, profiles=(sample_profile,))
    obs2 = SoilObservation(coordinate=sample_coordinate, profiles=(sample_profile,))

    c2 = Coordinate(0, 0)
    obs3 = SoilObservation(coordinate=c2, profiles=(sample_profile,))

    obs_set = {obs1, obs2, obs3}
    assert len(obs_set) == 2
    assert obs1 in obs_set
    assert obs3 in obs_set


def test_slots(sample_coordinate: Coordinate, sample_profile: SoilProfile) -> None:
    """Verify that SoilObservation has slots and no __dict__ representation."""
    obs = SoilObservation(coordinate=sample_coordinate, profiles=(sample_profile,))
    assert not hasattr(obs, "__dict__")
