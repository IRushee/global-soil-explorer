"""Integration tests verifying the expanded SQLite Repository functionality."""

import concurrent.futures
import random
from pathlib import Path

import pytest

from backend.domain import Coordinate, SoilObservation
from backend.repository.sqlite_repository import (
    SQLiteSoilObservationRepository,
)

DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "output" / "hwsd.db"


def test_expanded_repository_resolution() -> None:
    """Verify that retrieval constructs the full scientific value object graph."""
    if not DB_PATH.exists():
        pytest.skip("Generated SQLite database not found.")

    repo = SQLiteSoilObservationRepository(DB_PATH)

    # Resolve a known valid SMU key (1666)
    coord = Coordinate(34.0, -118.0)
    obs = repo.get_by_key(1666, coordinate=coord)

    # 1. Root level checks
    assert isinstance(obs, SoilObservation)
    assert obs.coordinate == coord
    assert obs.environmental_context is not None
    assert obs.environmental_context.koppen_climate is not None
    assert obs.metadata is not None
    assert obs.metadata.dataset_version == "v2.0"
    assert obs.metadata.reference_identifiers is not None
    assert len(obs.metadata.reference_identifiers) > 0

    # 2. Profile level checks
    assert len(obs.profiles) > 0
    profile = obs.profiles[0]
    assert profile.hydrologic_context is not None
    assert profile.hydrologic_context.drainage is not None
    assert profile.land_limitations is not None
    assert profile.classification is not None
    assert (
        profile.classification.wrb4_code is not None
        or profile.classification.wrb2_code is not None
    )

    # 3. Layer level checks
    assert len(profile.layers) > 0
    layer = profile.layers[0]
    assert layer.texture is not None
    assert layer.measurements is not None

    # Verify physical / chemical properties structure
    phys = layer.measurements.physical
    assert phys is not None
    chem = layer.measurements.chemical
    hyd = layer.measurements.hydraulic

    # Check presence of pH and Available Water Capacity
    assert chem.ph is None or (0.0 <= chem.ph <= 14.0)
    assert hyd.available_water_capacity is None or hyd.available_water_capacity >= 0.0


def test_repository_concurrency() -> None:
    """Verify the repository handles parallel reads safely across 100 worker threads."""
    if not DB_PATH.exists():
        pytest.skip("Database missing.")

    repo = SQLiteSoilObservationRepository(DB_PATH)

    # Grab 200 random SMU IDs from the database
    db_conn = repo._db_path
    import sqlite3

    c = sqlite3.connect(str(db_conn))
    cursor = c.cursor()
    cursor.execute(
        "SELECT DISTINCT HWSD2_SMU_ID FROM HWSD2_LAYERS WHERE HWSD2_SMU_ID IS NOT NULL LIMIT 200"
    )
    smu_ids = [row[0] for row in cursor.fetchall()]
    c.close()

    if not smu_ids:
        pytest.skip("No SMUs available in DB.")

    def worker_task(smu_id: int) -> int:
        obs = repo.get_by_key(smu_id)
        assert isinstance(obs, SoilObservation)
        return len(obs.profiles)

    # Run query loops concurrently
    queries = [random.choice(smu_ids) for _ in range(1000)]
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        results = list(executor.map(worker_task, queries))

    assert len(results) == 1000
    assert all(res > 0 for res in results)
