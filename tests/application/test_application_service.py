"""Integration and unit tests for the ApplicationService."""

import sqlite3
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from backend.application.exceptions import ApplicationServiceError
from backend.application.service import ApplicationService
from backend.contracts.repository import SoilObservationRepository
from backend.contracts.spatial_lookup import SpatialLookupService
from backend.domain import (
    Coordinate,
    SoilClassification,
    SoilLayer,
    SoilObservation,
    SoilProfile,
    SoilProperty,
)
from backend.domain.exceptions import InvalidCoordinateError, InvalidObservationError
from backend.repository.sqlite_repository import SQLiteSoilObservationRepository
from backend.spatial.raster_lookup import BILRasterSpatialLookupService

RAW_RASTER_DIR = Path("../data/raw/hwsd")
DB_PATH = Path("../data/output/hwsd.db")


# =====================================================================
# Unit & Mocked Infrastructure Tests
# =====================================================================


def test_application_service_di_success() -> None:
    """Verify that dependencies are correctly injected and coordinate flow works."""
    # 1. Setup mock coordinate, classification, layer, profile, observation
    coord = Coordinate(10.0, 20.0)
    classification = SoilClassification(
        taxonomy_standard="FAO 1990",
        class_symbol="ACf",
        class_name="Ferric Acrisols",
    )
    layer = SoilLayer(top_depth_cm=0.0, bottom_depth_cm=30.0, properties=())
    profile = SoilProfile(
        layers=(layer,), classification=classification, composition_share=100.0
    )
    mock_obs = SoilObservation(
        coordinate=Coordinate(0.0, 0.0), profiles=(profile,)
    )

    # 2. Setup mock dependencies
    mock_lookup = MagicMock(spec=SpatialLookupService)
    mock_lookup.resolve.return_value = 42

    mock_repo = MagicMock(spec=SoilObservationRepository)
    mock_repo.get_by_key.return_value = mock_obs

    # 3. Instantiate and run
    service = ApplicationService(mock_lookup, mock_repo)
    result = service.get_soil_observation(coord)

    # 4. Assertions
    assert result is not None
    assert isinstance(result, SoilObservation)
    assert result.coordinate == coord
    assert result.profiles == (profile,)
    mock_lookup.resolve.assert_called_once_with(coord)
    mock_repo.get_by_key.assert_called_once_with(42)


def test_application_service_no_mapping_unit() -> None:
    """Verify that if the spatial lookup resolves to None, None is returned."""
    coord = Coordinate(10.0, 20.0)
    mock_lookup = MagicMock(spec=SpatialLookupService)
    mock_lookup.resolve.return_value = None

    mock_repo = MagicMock(spec=SoilObservationRepository)

    service = ApplicationService(mock_lookup, mock_repo)
    result = service.get_soil_observation(coord)

    assert result is None
    mock_lookup.resolve.assert_called_once_with(coord)
    mock_repo.get_by_key.assert_not_called()


def test_application_service_key_not_found() -> None:
    """Verify that if the repository raises KeyError, None is returned."""
    coord = Coordinate(10.0, 20.0)
    mock_lookup = MagicMock(spec=SpatialLookupService)
    mock_lookup.resolve.return_value = 9999

    mock_repo = MagicMock(spec=SoilObservationRepository)
    mock_repo.get_by_key.side_effect = KeyError("Key 9999 not found.")

    service = ApplicationService(mock_lookup, mock_repo)
    result = service.get_soil_observation(coord)

    assert result is None
    mock_lookup.resolve.assert_called_once_with(coord)
    mock_repo.get_by_key.assert_called_once_with(9999)


def test_application_service_spatial_lookup_infrastructure_failure() -> None:
    """Verify that spatial lookup service failures raise ApplicationServiceError."""
    coord = Coordinate(10.0, 20.0)
    mock_lookup = MagicMock(spec=SpatialLookupService)
    mock_lookup.resolve.side_effect = OSError("Flat binary file read error")

    mock_repo = MagicMock(spec=SoilObservationRepository)

    service = ApplicationService(mock_lookup, mock_repo)

    with pytest.raises(ApplicationServiceError) as exc_info:
        service.get_soil_observation(coord)

    assert "Spatial lookup failed" in str(exc_info.value)
    mock_lookup.resolve.assert_called_once_with(coord)
    mock_repo.get_by_key.assert_not_called()


def test_application_service_repository_infrastructure_failure() -> None:
    """Verify that database failures raise ApplicationServiceError."""
    coord = Coordinate(10.0, 20.0)
    mock_lookup = MagicMock(spec=SpatialLookupService)
    mock_lookup.resolve.return_value = 42

    mock_repo = MagicMock(spec=SoilObservationRepository)
    mock_repo.get_by_key.side_effect = sqlite3.DatabaseError(
        "Database image is malformed"
    )

    service = ApplicationService(mock_lookup, mock_repo)

    with pytest.raises(ApplicationServiceError) as exc_info:
        service.get_soil_observation(coord)

    assert "Database query failed" in str(exc_info.value)
    mock_lookup.resolve.assert_called_once_with(coord)
    mock_repo.get_by_key.assert_called_once_with(42)


def test_application_service_domain_reconstruction_failure() -> None:
    """Verify that domain reconstruction errors raise ApplicationServiceError."""
    coord = Coordinate(10.0, 20.0)
    mock_lookup = MagicMock(spec=SpatialLookupService)
    mock_lookup.resolve.return_value = 42

    # Construct invalid observation (e.g. empty profiles list, raising InvalidObservationError)
    mock_obs = MagicMock(spec=SoilObservation)
    mock_obs.profiles = ()  # Empty profiles causes InvalidObservationError on reconstruction

    mock_repo = MagicMock(spec=SoilObservationRepository)
    mock_repo.get_by_key.return_value = mock_obs

    service = ApplicationService(mock_lookup, mock_repo)

    with pytest.raises(ApplicationServiceError) as exc_info:
        service.get_soil_observation(coord)

    assert "Failed to reconstruct" in str(exc_info.value)
    mock_lookup.resolve.assert_called_once_with(coord)
    mock_repo.get_by_key.assert_called_once_with(42)


# =====================================================================
# Real HWSD Dataset Integration Tests
# =====================================================================


def _hwsd_files_available() -> bool:
    """Check if the HWSD binary raster and database exist on disk."""
    bil_path = RAW_RASTER_DIR / "HWSD2.bil"
    hdr_path = RAW_RASTER_DIR / "HWSD2.hdr"
    return bil_path.exists() and hdr_path.exists() and DB_PATH.exists()


@pytest.mark.skipif(
    not _hwsd_files_available(), reason="HWSD raw files or database missing."
)
class TestHWSDIntegration:
    """Integration tests executing against the actual HWSD v2.0 dataset."""

    @pytest.fixture(autouse=True)
    def setup_service(self) -> None:
        """Initialize the real spatial lookup and sqlite repository services."""
        bil_path = RAW_RASTER_DIR / "HWSD2.bil"
        hdr_path = RAW_RASTER_DIR / "HWSD2.hdr"
        self.lookup_service = BILRasterSpatialLookupService(bil_path, hdr_path)
        self.repository = SQLiteSoilObservationRepository(DB_PATH)
        self.app_service = ApplicationService(
            self.lookup_service, self.repository
        )

        yield

        self.lookup_service.close()

    def test_integration_valid_land(self) -> None:
        """Verify that a valid land coordinate returns a fully populated SoilObservation."""
        coord = Coordinate(52.0, 10.0)  # Germany
        obs = self.app_service.get_soil_observation(coord)

        assert obs is not None
        assert isinstance(obs, SoilObservation)
        assert obs.coordinate == coord
        assert len(obs.profiles) > 0

        # Assert correct mapping unit resolution match with manual query
        # Coordinate(52.0, 10.0) should map to SMU 10221
        manual_obs = self.repository.get_by_key(10221)
        assert len(obs.profiles) == len(manual_obs.profiles)
        assert (
            obs.profiles[0].classification.class_symbol
            == manual_obs.profiles[0].classification.class_symbol
        )

    def test_integration_ocean(self) -> None:
        """Verify that ocean coordinates resolve to None (no observation)."""
        coord = Coordinate(0.0, -30.0)  # Atlantic Ocean
        obs = self.app_service.get_soil_observation(coord)
        assert obs is None

    def test_integration_glacier(self) -> None:
        """Verify that glacier coordinates resolve to a glacier profile."""
        coord = Coordinate(72.0, -40.0)  # Greenland
        obs = self.app_service.get_soil_observation(coord)

        assert obs is not None
        assert len(obs.profiles) == 1
        profile = obs.profiles[0]
        assert profile.classification.class_symbol == "GG"
        assert profile.classification.class_name == "Glaciers"

    def test_integration_urban(self) -> None:
        """Verify that urban/Technosols coordinates resolve successfully."""
        coord = Coordinate(41.9028, 12.4964)  # Rome, Italy
        obs = self.app_service.get_soil_observation(coord)

        assert obs is not None
        assert len(obs.profiles) > 0
        # Should contain Technosols class
        has_technosols = any(
            p.classification.class_symbol == "TC" for p in obs.profiles
        )
        assert has_technosols

    def test_integration_repeated_queries(self) -> None:
        """Verify that repeated queries on the same coordinate yield identical results."""
        coord = Coordinate(52.0, 10.0)

        obs1 = self.app_service.get_soil_observation(coord)
        obs2 = self.app_service.get_soil_observation(coord)

        assert obs1 is not None
        assert obs2 is not None
        assert obs1.coordinate == obs2.coordinate
        assert len(obs1.profiles) == len(obs2.profiles)

        for p1, p2 in zip(obs1.profiles, obs2.profiles):
            assert (
                p1.classification.class_symbol == p2.classification.class_symbol
            )
            assert p1.composition_share == p2.composition_share
            assert len(p1.layers) == len(p2.layers)

    def test_integration_out_of_bounds(self) -> None:
        """Verify that coordinates outside valid ranges fail validation."""
        # Using Coordinate constructor directly to ensure exception
        with pytest.raises(InvalidCoordinateError):
            Coordinate(95.0, 0.0)

        with pytest.raises(InvalidCoordinateError):
            Coordinate(0.0, 185.0)
