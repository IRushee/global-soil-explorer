# ruff: noqa
"""Production benchmarking script for the FastAPI REST API layer."""

import math
import resource
import statistics
import time
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

from backend.api.app import app

LATITUDE = 52.0
LONGITUDE = 10.0


def get_memory_usage_mb() -> float:
    """Return resident set size in megabytes."""
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    # on macOS ru_maxrss is in bytes
    return rss / (1024.0 * 1024.0)


def calculate_percentile(data: list[float], pct: float) -> float:
    """Compute percentile from raw float list."""
    if not data:
        return 0.0
    sorted_data = sorted(data)
    idx = (len(sorted_data) - 1) * pct
    f = math.floor(idx)
    c = math.ceil(idx)
    if f == c:
        return sorted_data[int(idx)]
    d0 = sorted_data[int(f)] * (c - idx)
    d1 = sorted_data[int(c)] * (idx - f)
    return d0 + d1


def run_benchmark(num_requests: int) -> dict[str, Any]:
    print(f"Benchmarking {num_requests} requests...")

    # Using context manager to trigger FastAPI startup lifespan events
    with TestClient(app) as client:
        # Warmup
        for _ in range(10):
            client.get("/soil", params={"latitude": LATITUDE, "longitude": LONGITUDE})

        mem_start = get_memory_usage_mb()
        start_time = time.perf_counter()

        latencies = []
        for _ in range(num_requests):
            t0 = time.perf_counter()
            client.get("/soil", params={"latitude": LATITUDE, "longitude": LONGITUDE})
            t1 = time.perf_counter()
            latencies.append((t1 - t0) * 1000.0)

        end_time = time.perf_counter()
        mem_end = get_memory_usage_mb()

    total_time_sec = end_time - start_time
    throughput = num_requests / total_time_sec if total_time_sec > 0 else 0.0

    return {
        "count": num_requests,
        "avg": statistics.mean(latencies),
        "median": statistics.median(latencies),
        "p95": calculate_percentile(latencies, 0.95),
        "p99": calculate_percentile(latencies, 0.99),
        "throughput": throughput,
        "memory_start_mb": mem_start,
        "memory_end_mb": mem_end,
        "memory_diff_mb": mem_end - mem_start,
    }


def print_report(res: dict[str, Any]) -> None:
    print(f"\n=== BENCHMARK FOR {res['count']} REQUESTS ===")
    print(f"Throughput:  {res['throughput']:.2f} req/sec")
    print(f"Latency:")
    print(f"  - Average: {res['avg']:.3f} ms")
    print(f"  - Median:  {res['median']:.3f} ms")
    print(f"  - P95:     {res['p95']:.3f} ms")
    print(f"  - P99:     {res['p99']:.3f} ms")
    print(f"Memory:")
    print(f"  - Start:   {res['memory_start_mb']:.2f} MB")
    print(f"  - End:     {res['memory_end_mb']:.2f} MB")
    print(f"  - Growth:  {res['memory_diff_mb']:.2f} MB")


def main() -> None:
    for count in [1, 100, 1000, 5000]:
        res = run_benchmark(count)
        print_report(res)


if __name__ == "__main__":
    main()
