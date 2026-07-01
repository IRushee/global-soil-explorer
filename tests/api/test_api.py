"""Integration tests for the FastAPI REST API layer."""

from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest
from backend.api.app import app
from backend.application.exceptions import ApplicationServiceError
from backend.application.service import ApplicationService
from fastapi.testclient import TestClient

RAW_RASTER_DIR = Path("../data/raw/hwsd")
DB_PATH = Path("../data/output/hwsd.db")


def _hwsd_files_available() -> bool:
    """Check if the HWSD binary raster and database exist on disk."""
    bil_path = RAW_RASTER_DIR / "HWSD2.bil"
    hdr_path = RAW_RASTER_DIR / "HWSD2.hdr"
    return bil_path.exists() and hdr_path.exists() and DB_PATH.exists()


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Fixture providing a test client with lifespan triggered."""
    if not _hwsd_files_available():
        pytest.skip("HWSD raw files or database missing.")

    # Using the with-block triggers FastAPI's lifespan (startup/shutdown)
    with TestClient(app) as test_client:
        yield test_client


def test_api_health_endpoint(client: TestClient) -> None:
    """Verify GET /health returns 200 and indicates fully healthy services."""
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert "runtime_version" in data
    assert data["dataset_name"] == "HWSD v2.0"
    assert data["dataset_version"] == "2.0"
    assert data["spatial_lookup_available"] is True
    assert data["repository_available"] is True
    assert data["database_available"] is True


def test_api_soil_valid_land(client: TestClient) -> None:
    """Verify GET /soil with valid land coordinate returns 200 and soil data."""
    # Germany: 52.0° N, 10.0° E
    response = client.get("/soil", params={"latitude": 52.0, "longitude": 10.0})
    assert response.status_code == 200

    data = response.json()
    assert "coordinate" in data
    assert data["coordinate"]["latitude"] == 52.0
    assert data["coordinate"]["longitude"] == 10.0
    assert "profiles" in data
    assert len(data["profiles"]) > 0

    profile = data["profiles"][0]
    assert "classification" in profile
    assert "taxonomy_standard" in profile["classification"]
    assert "class_symbol" in profile["classification"]["codes"]
    assert "class_name" in profile["classification"]

    assert "layers" in profile
    assert len(profile["layers"]) > 0

    layer = profile["layers"][0]
    assert "top_depth_cm" in layer
    assert "bottom_depth_cm" in layer
    assert "properties" in layer
    assert len(layer["properties"]) > 0

    prop = layer["properties"][0]
    assert "property_type" in prop
    assert "value" in prop
    assert "unit" in prop


def test_api_soil_ocean_returns_204(client: TestClient) -> None:
    """Verify GET /soil in the ocean resolves to None and returns 204 No Content."""
    # Atlantic Ocean: 0.0, -30.0
    response = client.get("/soil", params={"latitude": 0.0, "longitude": -30.0})
    assert response.status_code == 204
    assert response.text == ""  # No response body for 204


def test_api_soil_open_water_returns_wr(client: TestClient) -> None:
    """Verify GET /soil in Lake Victoria returns Open Water (WR) profile."""
    # Lake Victoria: -1.0° S, 33.0° E
    response = client.get("/soil", params={"latitude": -1.0, "longitude": 33.0})
    assert response.status_code == 200
    data = response.json()
    profiles = data["profiles"]
    assert len(profiles) > 0
    assert profiles[0]["classification"]["codes"]["class_symbol"] == "WR"
    assert profiles[0]["classification"]["class_name"] == "Open Water"


def test_api_soil_glacier_returns_gg(client: TestClient) -> None:
    """Verify GET /soil in Greenland resolves to a Glacier (GG) profile."""
    # Greenland: 72.0° N, -40.0° E
    response = client.get("/soil", params={"latitude": 72.0, "longitude": -40.0})
    assert response.status_code == 200

    data = response.json()
    profiles = data["profiles"]
    assert len(profiles) == 1
    assert profiles[0]["classification"]["codes"]["class_symbol"] == "GG"
    assert profiles[0]["classification"]["class_name"] == "Glaciers"


def test_api_soil_urban_returns_tc(client: TestClient) -> None:
    """Verify GET /soil in Rome returns a Technosols (TC) profile."""
    # Rome: 41.9028, 12.4964
    response = client.get("/soil", params={"latitude": 41.9028, "longitude": 12.4964})
    assert response.status_code == 200

    data = response.json()
    profiles = data["profiles"]
    assert len(profiles) > 0
    # At least one profile should contain Technosols class symbol "TC"
    symbols = [p["classification"]["codes"]["class_symbol"] for p in profiles]
    assert "TC" in symbols


def test_api_soil_coastline(client: TestClient) -> None:
    """Verify GET /soil near a coastline resolves successfully (either 200 or 204)."""
    # Santa Monica, CA Coast: 34.01, -118.50
    response = client.get("/soil", params={"latitude": 34.01, "longitude": -118.50})
    assert response.status_code in (200, 204)


def test_api_soil_invalid_coordinates(client: TestClient) -> None:
    """Verify GET /soil returns HTTP 400 for malformed or out-of-bounds inputs."""
    # Out of bounds latitude
    response = client.get("/soil", params={"latitude": 95.0, "longitude": 10.0})
    assert response.status_code == 400
    assert "Latitude must be between" in response.json()["detail"]

    # Out of bounds longitude
    response = client.get("/soil", params={"latitude": 52.0, "longitude": 185.0})
    assert response.status_code == 400
    assert "Longitude must be between" in response.json()["detail"]

    # Non-numeric query string parameters
    response = client.get("/soil", params={"latitude": "abc", "longitude": 10.0})
    assert response.status_code == 400
    assert "Invalid coordinate query parameters" in response.json()["detail"]

    # Missing query parameters
    response = client.get("/soil", params={"latitude": 52.0})
    assert response.status_code == 400
    assert "Invalid coordinate query parameters" in response.json()["detail"]


def test_api_soil_infrastructure_failure(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify GET /soil returns HTTP 503 on service failures."""

    def mock_get_soil_observation(self: ApplicationService, coord: Any) -> None:
        raise ApplicationServiceError("Mocked database lookup timeout failure.")

    monkeypatch.setattr(
        ApplicationService, "get_soil_observation", mock_get_soil_observation
    )

    response = client.get("/soil", params={"latitude": 52.0, "longitude": 10.0})
    assert response.status_code == 503
    assert "Mocked database lookup" in response.json()["detail"]


def test_api_soil_unexpected_failure(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify GET /soil returns HTTP 500 on unhandled exceptions."""

    def mock_get_soil_observation(self: ApplicationService, coord: Any) -> None:
        raise RuntimeError("Something went critically wrong in memory.")

    monkeypatch.setattr(
        ApplicationService, "get_soil_observation", mock_get_soil_observation
    )

    response = client.get("/soil", params={"latitude": 52.0, "longitude": 10.0})
    assert response.status_code == 500
    assert "An unexpected internal server error occurred." in response.json()["detail"]


def test_v1_api_health_endpoint(client: TestClient) -> None:
    """Verify GET /v1/health works identically to unversioned endpoint."""
    response = client.get("/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["dataset_name"] == "HWSD v2.0"


def test_v1_api_soil_valid_land(client: TestClient) -> None:
    """Verify GET /v1/soil works identically to unversioned endpoint."""
    response = client.get("/v1/soil", params={"latitude": 52.0, "longitude": 10.0})
    assert response.status_code == 200
    data = response.json()
    assert data["coordinate"]["latitude"] == 52.0
    assert len(data["profiles"]) > 0
    assert "codes" in data["profiles"][0]["classification"]
