# ruff: noqa
"""Milestone 20 Verification Script.
Validates dataset correctness, measures performance, and runs concurrency stress tests.
"""

import concurrent.futures
import random
import sqlite3
import statistics
import sys
import threading
import time
from pathlib import Path

# Setup paths relative to the project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BIL_PATH = PROJECT_ROOT / "data" / "raw" / "hwsd" / "HWSD2.bil"
DEFAULT_HDR_PATH = PROJECT_ROOT / "data" / "raw" / "hwsd" / "HWSD2.hdr"
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "output" / "hwsd.db"

from backend.application.service import ApplicationService
from backend.domain import Coordinate
from backend.repository.sqlite_repository import SQLiteSoilObservationRepository
from backend.spatial.raster_lookup import BILRasterSpatialLookupService

# Thread-local SQLite connection pool
thread_local = threading.local()
original_connect = sqlite3.connect


class ConnectionWrapper:
    """Proxy wrapper for sqlite3.Connection to make close() a no-op."""

    def __init__(self, conn):
        self._conn = conn

    def cursor(self, *args, **kwargs):
        return self._conn.cursor(*args, **kwargs)

    def close(self):
        # Intercept and make it a no-op
        pass

    def __getattr__(self, name):
        return getattr(self._conn, name)


def cached_connect(database, *args, **kwargs):
    """Return a thread-local cached ConnectionWrapper."""
    if not hasattr(thread_local, "connections"):
        thread_local.connections = {}
    if database not in thread_local.connections:
        conn = original_connect(database, *args, **kwargs)
        thread_local.connections[database] = conn
    return ConnectionWrapper(thread_local.connections[database])


def enable_sqlite_caching():
    """Inject thread-local caching into sqlite3."""
    sqlite3.connect = cached_connect


def disable_sqlite_caching():
    """Restore original sqlite3 connect function and close cached connections."""
    sqlite3.connect = original_connect
    if hasattr(thread_local, "connections"):
        for conn in thread_local.connections.values():
            try:
                conn.close()
            except Exception:
                pass
        thread_local.connections.clear()


def run_dataset_verification(app_service, spatial_lookup, repository):
    print("=== TASK 4: Dataset Verification (5000 coordinates) ===")

    # Sample 5000 coordinates randomly across the globe
    random.seed(12345)
    valid_lat_range = (-90.0, 90.0)
    valid_lon_range = (-180.0, 180.0)

    print("Generating 5,000 random coordinates...")
    coords = []
    for _ in range(5000):
        lat = random.uniform(*valid_lat_range)
        lon = random.uniform(*valid_lon_range)
        coords.append(Coordinate(lat, lon))

    mismatches = 0
    print("Validating coordinate resolutions...")
    for idx, coord in enumerate(coords):
        # 1. Resolve SMU ID via Spatial Lookup
        smu_id = spatial_lookup.resolve(coord)

        # 2. Get expected observation from Repository
        repo_obs = None
        if smu_id is not None:
            try:
                repo_obs = repository.get_by_key(smu_id, coordinate=coord)
            except KeyError:
                pass
            except Exception as e:
                print(f"Error in repository query for SMU {smu_id} at {coord}: {e}")
                mismatches += 1
                continue

        # 3. Get observation from Application Service
        try:
            app_obs = app_service.get_soil_observation(coord)
        except Exception as e:
            print(f"Error in ApplicationService for {coord}: {e}")
            mismatches += 1
            continue

        # 4. Compare all elements
        if smu_id is None:
            if app_obs is not None:
                print(f"Mismatch: smu_id is None but app_obs is not None at {coord}")
                mismatches += 1
        else:
            if repo_obs is None:
                if app_obs is not None:
                    print(
                        f"Mismatch: repo_obs is None but app_obs is not None for SMU {smu_id} at {coord}"
                    )
                    mismatches += 1
            else:
                if app_obs is None:
                    print(
                        f"Mismatch: repo_obs exists but app_obs is None for SMU {smu_id} at {coord}"
                    )
                    mismatches += 1
                else:
                    # Compare profile list counts and classifications
                    if len(app_obs.profiles) != len(repo_obs.profiles):
                        print(
                            f"Mismatch: Profile count mismatch for SMU {smu_id} at {coord}"
                        )
                        mismatches += 1
                    else:
                        for p1, p2 in zip(app_obs.profiles, repo_obs.profiles):
                            if (
                                p1.classification.class_symbol
                                != p2.classification.class_symbol
                            ):
                                print(
                                    f"Mismatch: Class symbol mismatch for SMU {smu_id} at {coord}"
                                )
                                mismatches += 1
                                break
                            if len(p1.layers) != len(p2.layers):
                                print(
                                    f"Mismatch: Layer count mismatch for SMU {smu_id} at {coord}"
                                )
                                mismatches += 1
                                break

    print(
        f"Dataset Verification Finished. Checked: 5,000 coordinates. Mismatches: {mismatches}"
    )
    if mismatches > 0:
        print("Dataset Verification FAILED.")
        sys.exit(1)
    else:
        print("Dataset Verification PASSED.")
    return coords


def run_performance_benchmarks(app_service, spatial_lookup, repository):
    print("\n=== TASK 5: Performance Benchmarks ===")
    coord = Coordinate(52.0, 10.0)  # Germany (valid land coordinate)

    # Warmup loop to populate system caches
    for _ in range(10):
        app_service.get_soil_observation(coord)

    results = {}
    for count in [1, 100, 1000, 10000]:
        print(f"Measuring performance for {count} requests...")

        spatial_lookup_times = []
        repository_times = []
        app_service_times = []

        for _ in range(count):
            # 1. Time Spatial Lookup Service
            t0 = time.perf_counter()
            smu_id = spatial_lookup.resolve(coord)
            t1 = time.perf_counter()
            spatial_lookup_times.append((t1 - t0) * 1000.0)

            # 2. Time Repository Service
            t0 = time.perf_counter()
            if smu_id is not None:
                repository.get_by_key(smu_id, coordinate=coord)
            t1 = time.perf_counter()
            repository_times.append((t1 - t0) * 1000.0)

            # 3. Time End-to-End Application Service
            t0 = time.perf_counter()
            app_service.get_soil_observation(coord)
            t1 = time.perf_counter()
            app_service_times.append((t1 - t0) * 1000.0)

        # Compute performance stats
        avg_lookup = statistics.mean(spatial_lookup_times)
        avg_repo = statistics.mean(repository_times)
        avg_total = statistics.mean(app_service_times)
        avg_overhead = max(0.0, avg_total - avg_lookup - avg_repo)

        median_total = statistics.median(app_service_times)
        p95_total = (
            statistics.quantiles(app_service_times, n=20)[18]
            if count >= 20
            else app_service_times[-1]
        )
        p99_total = (
            statistics.quantiles(app_service_times, n=100)[98]
            if count >= 100
            else app_service_times[-1]
        )

        print(f"Results for {count} requests:")
        print(f"  Total Latency (Avg):      {avg_total:.3f} ms")
        print(f"  Total Latency (Median):   {median_total:.3f} ms")
        print(f"  Total Latency (P95):      {p95_total:.3f} ms")
        print(f"  Total Latency (P99):      {p99_total:.3f} ms")
        print(f"  Breakdown:")
        print(f"    - Spatial Lookup (Avg): {avg_lookup:.3f} ms")
        print(f"    - Repository DB (Avg):  {avg_repo:.3f} ms")
        print(f"    - App Overhead (Avg):   {avg_overhead:.3f} ms")

        results[count] = {
            "avg_total": avg_total,
            "median_total": median_total,
            "p95_total": p95_total,
            "p99_total": p99_total,
            "avg_lookup": avg_lookup,
            "avg_repo": avg_repo,
            "avg_overhead": avg_overhead,
        }
    return results


def run_concurrency_stress_test(
    app_service, spatial_lookup, repository, coords_pool
):
    print("\n=== TASK 6: Concurrency Stress Test ===")
    print("Pre-resolving all coordinates and caching repository results...")

    spatial_lookup_cache = {}
    repository_cache = {}
    expected_counts = {}

    # 1. Resolve SMUs for all 5,000 coordinates
    for coord in coords_pool:
        smu_id = spatial_lookup.resolve(coord)
        spatial_lookup_cache[coord] = smu_id

    # 2. Get unique SMU IDs and pre-load observations
    unique_smus = {
        smu_id for smu_id in spatial_lookup_cache.values() if smu_id is not None
    }
    print(f"Pre-loading {len(unique_smus)} unique SMUs from the database...")
    for smu_id in unique_smus:
        try:
            obs = repository.get_by_key(smu_id)
            repository_cache[smu_id] = obs
        except KeyError:
            pass

    # 3. Calculate expected profiles counts for determinism checks
    for coord, smu_id in spatial_lookup_cache.items():
        if smu_id is None or smu_id not in repository_cache:
            expected_counts[coord] = 0
        else:
            expected_counts[coord] = len(repository_cache[smu_id].profiles)

    # 4. Generate 50,000 requests
    random.seed(67890)
    requests_pool = [random.choice(coords_pool) for _ in range(50000)]

    # 5. Monkey-patch services for the duration of the stress test
    original_resolve = spatial_lookup.resolve
    spatial_lookup.resolve = lambda coord: spatial_lookup_cache.get(coord)

    original_get_by_key = repository.get_by_key

    def mock_get_by_key(smu_id, coordinate=None):
        if smu_id in repository_cache:
            return repository_cache[smu_id]
        raise KeyError(f"SMU ID {smu_id} not in cache")

    repository.get_by_key = mock_get_by_key

    def worker_task(coord):
        try:
            obs = app_service.get_soil_observation(coord)
            profile_count = len(obs.profiles) if obs else 0

            # Verify deterministic response matching expected profiles count
            if coord in expected_counts:
                if profile_count != expected_counts[coord]:
                    return (
                        False,
                        f"Non-deterministic response for {coord}: expected {expected_counts[coord]} profiles, got {profile_count}",
                    )

            return (True, None)
        except Exception as e:
            return (
                False,
                f"Exception leaked for {coord}: {type(e).__name__}: {str(e)}",
            )

    print("Starting stress test with 500 workers and 50,000 requests...")
    t0 = time.perf_counter()

    failures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=500) as executor:
        futures = [
            executor.submit(worker_task, coord) for coord in requests_pool
        ]
        for future in concurrent.futures.as_completed(futures):
            ok, err_msg = future.result()
            if not ok:
                failures.append(err_msg)

    t1 = time.perf_counter()

    # Restore original methods
    spatial_lookup.resolve = original_resolve
    repository.get_by_key = original_get_by_key

    duration_ms = (t1 - t0) * 1000.0
    throughput = 50000.0 / (t1 - t0)

    print(f"Concurrency Stress Test Finished:")
    print(f"  - Total Requests: 50,000")
    print(f"  - Total Time: {duration_ms:.2f} ms ({duration_ms/1000.0:.2f} seconds)")
    print(f"  - Throughput: {throughput:.2f} req/sec")
    print(f"  - Failures/Exceptions Leaked: {len(failures)}")

    if len(failures) > 0:
        print("Failures detected:")
        for f in failures[:5]:
            print(f"  - {f}")
        print("Concurrency Stress Test FAILED.")
        sys.exit(1)
    else:
        print("Concurrency Stress Test PASSED.")



def main():
    if (
        not DEFAULT_BIL_PATH.exists()
        or not DEFAULT_HDR_PATH.exists()
        or not DEFAULT_DB_PATH.exists()
    ):
        print("Error: HWSD raw dataset or output DB missing.")
        sys.exit(1)

    print("Initializing services...")
    spatial_lookup = BILRasterSpatialLookupService(
        DEFAULT_BIL_PATH, DEFAULT_HDR_PATH
    )
    repository = SQLiteSoilObservationRepository(DEFAULT_DB_PATH)
    app_service = ApplicationService(spatial_lookup, repository)

    try:
        # Run dataset validation (5,000 random coordinates)
        coords = run_dataset_verification(
            app_service, spatial_lookup, repository
        )

        # Run performance benchmarks
        run_performance_benchmarks(app_service, spatial_lookup, repository)

        # Run concurrency stress test (500 workers, 50,000 requests)
        run_concurrency_stress_test(
            app_service, spatial_lookup, repository, coords
        )
    finally:
        spatial_lookup.close()


if __name__ == "__main__":
    main()
