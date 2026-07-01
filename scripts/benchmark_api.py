"""Performance benchmarking script for the FastAPI REST API layer."""

import statistics
import time
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

from backend.api.app import app
from backend.domain import Coordinate

# Coords for Germany (valid land)
LATITUDE = 52.0
LONGITUDE = 10.0


def run_benchmark(num_requests: int) -> dict[str, Any]:
    print(f"Running benchmark with {num_requests} requests...")

    api_latencies = []
    app_service_latencies = []
    lookup_latencies = []
    repo_latencies = []

    # Using the TestClient as a context manager triggers FastAPI's lifespan
    with TestClient(app) as client:
        # Retrieve initialized services from app state
        spatial_lookup = app.state.spatial_lookup
        repository = app.state.repository
        app_service = app.state.application_service

        # Warmup loop to prepare SQLite caches
        for _ in range(10):
            client.get("/soil", params={"latitude": LATITUDE, "longitude": LONGITUDE})

        coord = Coordinate(LATITUDE, LONGITUDE)

        for _ in range(num_requests):
            # 1. Measure E2E API Call
            t0 = time.perf_counter()
            client.get("/soil", params={"latitude": LATITUDE, "longitude": LONGITUDE})
            t1 = time.perf_counter()
            api_latencies.append((t1 - t0) * 1000.0)  # ms

            # 2. Measure Application Service
            t0 = time.perf_counter()
            app_service.get_soil_observation(coord)
            t1 = time.perf_counter()
            app_service_latencies.append((t1 - t0) * 1000.0)

            # 3. Measure Spatial Lookup
            t0 = time.perf_counter()
            smu_id = spatial_lookup.resolve(coord)
            t1 = time.perf_counter()
            lookup_latencies.append((t1 - t0) * 1000.0)

            # 4. Measure Repository DB Query (using same SMU_ID resolved above)
            if smu_id is not None:
                t0 = time.perf_counter()
                repository.get_by_key(smu_id)
                t1 = time.perf_counter()
                repo_latencies.append((t1 - t0) * 1000.0)

    # Compute statistics
    avg_api = statistics.mean(api_latencies)
    avg_app = statistics.mean(app_service_latencies)
    avg_lookup = statistics.mean(lookup_latencies)
    avg_repo = statistics.mean(repo_latencies)

    # FastAPI Overhead = API latency - App Service latency
    avg_overhead = max(0.0, avg_api - avg_app)

    return {
        "count": num_requests,
        "api": {
            "mean": avg_api,
            "median": statistics.median(api_latencies),
            "min": min(api_latencies),
            "max": max(api_latencies),
            "p95": statistics.quantiles(api_latencies, n=20)[18],  # 95th percentile
        },
        "app_service": avg_app,
        "spatial_lookup": avg_lookup,
        "repository": avg_repo,
        "fastapi_overhead": avg_overhead,
    }


def format_results(res: dict[str, Any]) -> None:
    print(f"\n=== RESULTS FOR {res['count']} REQUESTS ===")
    print(
        f"API E2E Latency:      "
        f"Avg: {res['api']['mean']:.3f} ms | "
        f"Median: {res['api']['median']:.3f} ms | "
        f"Min: {res['api']['min']:.3f} ms | "
        f"Max: {res['api']['max']:.3f} ms | "
        f"95th: {res['api']['p95']:.3f} ms"
    )
    print(f"Breakdown:")
    print(f"  - FastAPI Overhead:  {res['fastapi_overhead']:.3f} ms")
    print(f"  - ApplicationService: {res['app_service']:.3f} ms")
    print(f"    - Spatial Lookup:  {res['spatial_lookup']:.3f} ms")
    print(f"    - Repository DB:   {res['repository']:.3f} ms")


if __name__ == "__main__":
    r100 = run_benchmark(100)
    format_results(r100)

    r1000 = run_benchmark(1000)
    format_results(r1000)
