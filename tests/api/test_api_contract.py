"""API contract tests verifying schema structure, versioning, and scientific purity."""

from pathlib import Path
from typing import Any

import pytest
from backend.api.app import app
from fastapi.testclient import TestClient

RAW_RASTER_DIR = Path("../data/raw/hwsd")
DB_PATH = Path("../data/output/hwsd.db")


def _hwsd_files_available() -> bool:
    """Check if the HWSD binary raster and database exist on disk."""
    bil_path = RAW_RASTER_DIR / "HWSD2.bil"
    hdr_path = RAW_RASTER_DIR / "HWSD2.hdr"
    return bil_path.exists() and hdr_path.exists() and DB_PATH.exists()


@pytest.fixture
def client() -> Any:
    """Fixture providing a test client with lifespan triggered."""
    if not _hwsd_files_available():
        pytest.skip("HWSD raw files or database missing.")

    with TestClient(app) as test_client:
        yield test_client


def test_api_contract_scientific_purity(client: TestClient) -> None:
    """Verify response payload does not leak database or internal structural details."""
    response = client.get("/v1/soil", params={"latitude": 52.0, "longitude": 10.0})
    assert response.status_code == 200

    data = response.json()

    # Define prohibited implementation / persistence / SQL terms (leakage checks)
    prohibited_keywords = [
        "hwsd2_smu_id",
        "hwsd2_layers",
        "sqlite",
        "sql",
        "database",
        "db_path",
        "conn",
        "cursor",
        "rowid",
        "raster_offset",
        "smu_index",
        "pixel",
    ]

    def scan_for_prohibited_terms(obj: Any) -> None:
        if isinstance(obj, dict):
            for k, v in obj.items():
                # Check key names
                lower_k = str(k).lower()
                for keyword in prohibited_keywords:
                    assert keyword not in lower_k, f"Leaked internal terminology: '{k}'"

                # Check string values for sensitive leaked identifiers
                if isinstance(v, str):
                    lower_v = v.lower()
                    for keyword in prohibited_keywords:
                        # Exclude harmless matches (e.g. data source naming)
                        if keyword in lower_v and "hwsd v2.0 database" not in lower_v:
                            assert False, f"Leaked internal value: '{v}' for key '{k}'"
                scan_for_prohibited_terms(v)
        elif isinstance(obj, list):
            for item in obj:
                scan_for_prohibited_terms(item)

    scan_for_prohibited_terms(data)


def test_api_contract_grouped_codes(client: TestClient) -> None:
    """Verify raw codes are grouped strictly in sub-objects named 'codes'."""
    response = client.get("/v1/soil", params={"latitude": 52.0, "longitude": 10.0})
    assert response.status_code == 200

    data = response.json()

    # 1. Dataset metadata codes grouping
    assert "metadata" in data
    meta = data["metadata"]
    assert "codes" in meta
    assert "coverage" in meta["codes"]
    assert "coverage" not in meta  # Coverage code is moved to codes block

    # 2. Profiles classification codes grouping
    profiles = data["profiles"]
    assert len(profiles) > 0
    profile = profiles[0]

    classification = profile["classification"]
    assert "codes" in classification
    assert "class_symbol" in classification["codes"]
    assert "wrb4_code" in classification["codes"]
    assert "class_symbol" not in classification  # Moved to codes block

    # 3. Hydrologic context codes grouping
    hydrologic = profile["hydrologic_context"]
    assert "codes" in hydrologic
    assert "drainage" in hydrologic["codes"]
    assert "water_regime" in hydrologic["codes"]
    assert "impermeable_layer" in hydrologic["codes"]
    assert "drainage" not in hydrologic  # Moved to codes block

    # 4. Land limitations codes grouping
    limitations = profile["land_limitations"]
    assert "codes" in limitations
    assert "root_depth" in limitations["codes"]
    assert "root_obstacles" in limitations["codes"]
    assert "root_depth" not in limitations  # Moved to codes block

    # 5. Layers texture codes grouping
    assert "layers" in profile
    assert len(profile["layers"]) > 0
    layer = profile["layers"][0]

    texture = layer["texture"]
    assert "codes" in texture
    assert "usda_texture" in texture["codes"]
    assert "soter_texture" in texture["codes"]
    assert "usda_texture" not in texture  # Moved to codes block


def test_api_contract_deprecation_duplication(client: TestClient) -> None:
    """Verify deprecated duplication fields are properly signaled in schema."""
    # Retrieve the OpenAPI spec directly to verify Pydantic schema deprecation markup
    response = client.get("/openapi.json")
    assert response.status_code == 200

    openapi = response.json()

    # Verify SoilLayerSchema properties deprecation
    schemas = openapi["components"]["schemas"]
    assert "SoilLayerSchema" in schemas
    layer_schema = schemas["SoilLayerSchema"]

    assert "properties" in layer_schema["properties"]
    prop_field = layer_schema["properties"]["properties"]

    # In OpenAPI 3.1.0/Pydantic v2, deprecated fields are marked with a 'deprecated' attribute
    assert prop_field.get("deprecated") is True or "deprecated" in prop_field
