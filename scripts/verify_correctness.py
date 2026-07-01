# ruff: noqa
"""Correctness audit script validating API against Application, Repository, SQLite, and MDB."""

import csv
import io
import random
import sqlite3
import subprocess
import sys
from pathlib import Path

from backend.api.app import app
from backend.application.service import ApplicationService
from backend.domain import Coordinate
from backend.repository.sqlite_repository import SQLiteSoilObservationRepository
from backend.spatial.raster_lookup import BILRasterSpatialLookupService
from fastapi.testclient import TestClient

RAW_RASTER_DIR = Path("../data/raw/hwsd")
MDB_PATH = Path("../data/raw/hwsd/HWSD2.mdb")
DB_PATH = Path("../data/output/hwsd.db")

# Constants to satisfy Ruff PLR2004
HTTP_200 = 200
HTTP_204 = 204
NUM_SAMPLES = 1000
NUM_COASTLINE = 100
PIXEL_SIZE = 0.0083333

MIN_LAT = -90.0
MAX_LAT = 90.0
MIN_LON = -180.0
MAX_LON = 180.0


MDB_LAYERS_CACHE: dict[int, list[dict[str, str]]] = {}


def preload_mdb_layers(mdb_path: Path) -> None:
    """Preload all layers from HWSD2_LAYERS in the MDB into memory cache."""
    global MDB_LAYERS_CACHE
    if not mdb_path.exists():
        return
    print("Preloading HWSD2_LAYERS from MDB database...")
    cmd = ["mdb-export", "-0", "NULL", str(mdb_path), "HWSD2_LAYERS"]
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    if proc.stdout is None:
        return

    header_line = proc.stdout.readline()
    if not header_line:
        proc.terminate()
        return

    reader = csv.reader(io.StringIO(header_line))
    headers = next(reader)
    smu_col_idx = -1
    for i, h in enumerate(headers):
        if h.upper() == "HWSD2_SMU_ID":
            smu_col_idx = i
            break
    if smu_col_idx == -1:
        smu_col_idx = 1

    csv_reader = csv.reader(proc.stdout)
    for row in csv_reader:
        if not row:
            continue
        try:
            smu_id = int(row[smu_col_idx])
        except ValueError:
            continue
        row_dict = dict(zip(headers, row))
        if smu_id not in MDB_LAYERS_CACHE:
            MDB_LAYERS_CACHE[smu_id] = []
        MDB_LAYERS_CACHE[smu_id].append(row_dict)

    proc.terminate()
    print(f"Preloaded {len(MDB_LAYERS_CACHE)} SMU layer maps from MDB.")


def verify_ocean_coordinate(
    client: TestClient,
    app_service: ApplicationService,
    lat: float,
    lon: float,
) -> tuple[bool, str]:
    """Verify API and service behavior for an ocean coordinate."""
    coord = Coordinate(lat, lon)
    api_res = client.get("/soil", params={"latitude": lat, "longitude": lon})
    if api_res.status_code != HTTP_204:
        return (
            False,
            f"Ocean coord ({lat}, {lon}) API expected 204, got {api_res.status_code}",
        )
    obs = app_service.get_soil_observation(coord)
    if obs is not None:
        return (
            False,
            f"Ocean coord ({lat}, {lon}) AppService expected None, got observation",
        )
    return True, "Ocean ok"


def verify_land_coordinate(
    client: TestClient,
    repository: SQLiteSoilObservationRepository,
    app_service: ApplicationService,
    smu_id: int,
    lat: float,
    lon: float,
) -> tuple[bool, str]:
    """Verify API, service, DB and MDB correctness for a land coordinate."""
    coord = Coordinate(lat, lon)
    api_res = client.get("/soil", params={"latitude": lat, "longitude": lon})
    if api_res.status_code != HTTP_200:
        return (
            False,
            f"Land coord ({lat}, {lon}) API expected 200, got {api_res.status_code}",
        )

    api_json = api_res.json()
    obs = app_service.get_soil_observation(coord)
    if obs is None:
        return (
            False,
            f"Land coord ({lat}, {lon}) AppService expected Observation, got None",
        )

    # Check coordinate serialization
    if (
        api_json["coordinate"]["latitude"] != obs.coordinate.latitude
        or api_json["coordinate"]["longitude"] != obs.coordinate.longitude
    ):
        return False, "API coordinate mismatch with ApplicationService"

    # Check profiles serialization count
    if len(api_json["profiles"]) != len(obs.profiles):
        return False, "API profiles count mismatch with ApplicationService"

    # Repository comparison
    repo_obs = repository.get_by_key(smu_id, coord)
    if len(obs.profiles) != len(repo_obs.profiles):
        return (
            False,
            "ApplicationService profiles count mismatch with Repository",
        )

    # Direct SQLite verification
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute(
        "SELECT SEQUENCE, SHARE, TOPDEP, BOTDEP FROM HWSD2_LAYERS "
        "WHERE HWSD2_SMU_ID = ? ORDER BY SEQUENCE, TOPDEP",
        (smu_id,),
    )
    sql_rows = cursor.fetchall()
    conn.close()

    if not sql_rows:
        return False, f"SQLite returned 0 rows for SMU {smu_id}"

    sql_sequences = set(r[0] for r in sql_rows)
    if len(sql_sequences) != len(repo_obs.profiles):
        return (
            False,
            f"SQLite sequences mismatch with Repository profiles "
            f"({len(sql_sequences)} vs {len(repo_obs.profiles)})",
        )

    # Direct MDB verification
    if MDB_PATH.exists():
        mdb_rows = MDB_LAYERS_CACHE.get(smu_id, [])
        if not mdb_rows:
            return False, f"MDB returned 0 rows for SMU {smu_id}"
        if len(mdb_rows) != len(sql_rows):
            return (
                False,
                f"MDB rows count ({len(mdb_rows)}) mismatch with "
                f"SQLite rows count ({len(sql_rows)})",
            )

    return True, "Land ok"


def collect_coordinates(
    spatial_lookup: BILRasterSpatialLookupService,
) -> tuple[list[tuple[float, float, int]], list[tuple[float, float]]]:
    """Collect land and ocean coordinate samples."""
    land_coords: list[tuple[float, float, int]] = []
    ocean_coords: list[tuple[float, float]] = []
    random.seed(42)

    while len(land_coords) < NUM_SAMPLES or len(ocean_coords) < NUM_SAMPLES:
        lat = random.uniform(MIN_LAT, MAX_LAT)
        lon = random.uniform(MIN_LON, MAX_LON)
        coord = Coordinate(lat, lon)
        try:
            smu_id = spatial_lookup.resolve(coord)
            if smu_id is not None:
                if len(land_coords) < NUM_SAMPLES:
                    land_coords.append((lat, lon, smu_id))
            elif len(ocean_coords) < NUM_SAMPLES:
                ocean_coords.append((lat, lon))
        except Exception:
            pass
    return land_coords, ocean_coords


def collect_coastline_pairs(
    spatial_lookup: BILRasterSpatialLookupService,
    land_coords: list[tuple[float, float, int]],
) -> list[tuple[tuple[float, float], tuple[float, float]]]:
    """Find adjacent land/ocean pixels forming coastline pairs."""
    coastline_pairs: list[tuple[tuple[float, float], tuple[float, float]]] = []
    for lat, lon, _ in land_coords:
        if len(coastline_pairs) >= NUM_COASTLINE:
            break
        for dlat, dlon in [
            (PIXEL_SIZE, 0.0),
            (-PIXEL_SIZE, 0.0),
            (0.0, PIXEL_SIZE),
            (0.0, -PIXEL_SIZE),
        ]:
            adj_lat = lat + dlat
            adj_lon = lon + dlon
            if (
                MIN_LAT <= adj_lat <= MAX_LAT
                and MIN_LON <= adj_lon <= MAX_LON
            ):
                adj_coord = Coordinate(adj_lat, adj_lon)
                try:
                    adj_smu = spatial_lookup.resolve(adj_coord)
                    if adj_smu is None:
                        coastline_pairs.append(
                            ((lat, lon), (adj_lat, adj_lon))
                        )
                        break
                except Exception:
                    pass
    return coastline_pairs


def main() -> None:
    print("=== STARTING CORRECTNESS AUDIT ===")

    bil_path = RAW_RASTER_DIR / "HWSD2.bil"
    hdr_path = RAW_RASTER_DIR / "HWSD2.hdr"

    if (
        not bil_path.exists()
        or not hdr_path.exists()
        or not DB_PATH.exists()
    ):
        print("Error: HWSD raw files or database missing.")
        sys.exit(1)

    spatial_lookup = BILRasterSpatialLookupService(bil_path, hdr_path)
    repository = SQLiteSoilObservationRepository(DB_PATH)
    app_service = ApplicationService(spatial_lookup, repository)

    # 1. Collect coordinates
    print("Collecting 1000 Land and 1000 Ocean coordinates...")
    land_coords, ocean_coords = collect_coordinates(spatial_lookup)

    # 2. Collect coastline pairs
    print("Collecting 100 Coastline pairs...")
    coastline_pairs = collect_coastline_pairs(spatial_lookup, land_coords)

    # 3. Environment specs
    environments = {
        "Glacier (Greenland)": (72.0, -40.0),
        "Urban (Rome)": (41.9028, 12.4964),
        "Water (Lake Victoria)": (-1.0, 33.0),
        "Desert (Sahara)": (25.0, 15.0),
        "Tropical Forest (Congo)": (-1.0, 20.0),
    }

    total_checks = 0
    passed_checks = 0

    preload_mdb_layers(MDB_PATH)

    with TestClient(app) as client:
        # Land Audit
        print("\nAuditing 1000 Land coordinates...")
        for idx, (lat, lon, smu_id) in enumerate(land_coords):
            ok, msg = verify_land_coordinate(
                client, repository, app_service, smu_id, lat, lon
            )
            total_checks += 1
            if ok:
                passed_checks += 1
            else:
                print(f"Fail at land index {idx}: {msg}")

        # Ocean Audit
        print("Auditing 1000 Ocean coordinates...")
        for idx, (lat, lon) in enumerate(ocean_coords):
            ok, msg = verify_ocean_coordinate(client, app_service, lat, lon)
            total_checks += 1
            if ok:
                passed_checks += 1
            else:
                print(f"Fail at ocean index {idx}: {msg}")

        # Coastline Audit
        print("Auditing 100 Coastline pairs...")
        for idx, (land, ocean) in enumerate(coastline_pairs):
            # We need to resolve land's SMU ID
            land_smu = spatial_lookup.resolve(Coordinate(land[0], land[1]))
            if land_smu is None:
                print(f"Fail at coastline land index {idx}: resolved to None")
                total_checks += 2
                continue
            ok1, msg1 = verify_land_coordinate(
                client, repository, app_service, land_smu, land[0], land[1]
            )
            ok2, msg2 = verify_ocean_coordinate(
                client, app_service, ocean[0], ocean[1]
            )
            total_checks += 2
            if ok1 and ok2:
                passed_checks += 2
            else:
                print(f"Fail at coastline pair index {idx}: {msg1} | {msg2}")

        # Specific Environments Audit
        print("Auditing specific environment coordinates...")
        for name, (lat, lon) in environments.items():
            coord = Coordinate(lat, lon)
            smu_id = spatial_lookup.resolve(coord)
            if smu_id is None:
                ok, msg = verify_ocean_coordinate(client, app_service, lat, lon)
            else:
                ok, msg = verify_land_coordinate(
                    client, repository, app_service, smu_id, lat, lon
                )
            total_checks += 1
            if ok:
                passed_checks += 1
                print(f"  ✓ {name}: Passed")
            else:
                print(f"  ✗ {name}: Failed ({msg})")

    spatial_lookup.close()

    print("\n=== CORRECTNESS AUDIT REPORT ===")
    print(f"Total Coordinates Verified: {total_checks}")
    print(f"Passed Checks:              {passed_checks}")
    print(
        f"Audit Result:               "
        f"{'SUCCESS' if passed_checks == total_checks else 'FAILED'}"
    )


if __name__ == "__main__":
    main()
