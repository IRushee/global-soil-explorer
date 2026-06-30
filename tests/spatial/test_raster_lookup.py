"""Unit and integration tests for the BILRasterSpatialLookupService."""

import concurrent.futures
from pathlib import Path

import pytest
from backend.domain import Coordinate
from backend.domain.exceptions import InvalidCoordinateError
from backend.spatial.raster_lookup import BILRasterSpatialLookupService

RAW_RASTER_DIR = Path("../data/raw/hwsd")


def test_raster_lookup_files_not_found() -> None:
    """Verify lookup service raises FileNotFoundError if paths are missing."""
    with pytest.raises(FileNotFoundError):
        BILRasterSpatialLookupService("nonexistent.bil", "nonexistent.hdr")


def test_raster_lookup_success() -> None:
    """Verify that a valid coordinate on land successfully returns an SMU_ID."""
    bil_path = RAW_RASTER_DIR / "HWSD2.bil"
    hdr_path = RAW_RASTER_DIR / "HWSD2.hdr"

    if not bil_path.exists() or not hdr_path.exists():
        pytest.skip("HWSD v2.0 raw dataset files not found.")

    service = BILRasterSpatialLookupService(bil_path, hdr_path)
    try:
        # Query Rome, Italy (approx 41.9028 N, 12.4964 E)
        coord = Coordinate(41.9028, 12.4964)
        smu_id = service.resolve(coord)
        assert smu_id is not None
        assert isinstance(smu_id, int)
        assert smu_id > 0
    finally:
        service.close()


def test_raster_lookup_ocean_returns_none() -> None:
    """Verify that coordinates in the ocean resolve to None (NoData)."""
    bil_path = RAW_RASTER_DIR / "HWSD2.bil"
    hdr_path = RAW_RASTER_DIR / "HWSD2.hdr"

    if not bil_path.exists():
        pytest.skip("HWSD v2.0 raw dataset files not found.")

    service = BILRasterSpatialLookupService(bil_path, hdr_path)
    try:
        # Middle of the Atlantic Ocean
        coord = Coordinate(0.0, -30.0)
        smu_id = service.resolve(coord)
        assert smu_id is None
    finally:
        service.close()


def test_raster_lookup_out_of_bounds() -> None:
    """Verify that coordinates outside geographic limits raise errors."""
    with pytest.raises(InvalidCoordinateError):
        Coordinate(95.0, 0.0)

    with pytest.raises(InvalidCoordinateError):
        Coordinate(0.0, 185.0)


def test_raster_lookup_boundaries() -> None:
    """Verify coordinates on grid boundaries resolve or return None."""
    bil_path = RAW_RASTER_DIR / "HWSD2.bil"
    hdr_path = RAW_RASTER_DIR / "HWSD2.hdr"

    if not bil_path.exists():
        pytest.skip("HWSD v2.0 raw dataset files not found.")

    service = BILRasterSpatialLookupService(bil_path, hdr_path)
    try:
        # Exact upper-left boundary
        assert service.resolve(Coordinate(90.0, -180.0)) is None
        # Exact lower-right boundary
        assert service.resolve(Coordinate(-90.0, 180.0)) is None
    finally:
        service.close()


def test_raster_lookup_repeatability() -> None:
    """Verify querying the same coordinate multiple times yields match."""
    bil_path = RAW_RASTER_DIR / "HWSD2.bil"
    hdr_path = RAW_RASTER_DIR / "HWSD2.hdr"

    if not bil_path.exists():
        pytest.skip("HWSD v2.0 raw dataset files not found.")

    service = BILRasterSpatialLookupService(bil_path, hdr_path)
    try:
        coord = Coordinate(41.9028, 12.4964)
        val1 = service.resolve(coord)
        val2 = service.resolve(coord)
        assert val1 == val2
    finally:
        service.close()


def test_raster_lookup_thread_safety() -> None:
    """Verify concurrent thread-safe access on the shared file handle."""
    bil_path = RAW_RASTER_DIR / "HWSD2.bil"
    hdr_path = RAW_RASTER_DIR / "HWSD2.hdr"

    if not bil_path.exists():
        pytest.skip("HWSD v2.0 raw dataset files not found.")

    service = BILRasterSpatialLookupService(bil_path, hdr_path)
    coords = [Coordinate(41.9028 + (i * 0.0001), 12.4964) for i in range(100)]

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            # Query concurrently
            results = list(executor.map(service.resolve, coords))

        assert len(results) == 100
        # Check that we got numeric values or None correctly
        for r in results:
            assert r is None or isinstance(r, int)
    finally:
        service.close()
