# ruff: noqa
"""Scale benchmarking script for the expanded SQLite repository."""

import random
import resource
import sqlite3
import statistics
import sys
import time
from pathlib import Path

from backend.repository.sqlite_repository import (
    SQLiteSoilObservationRepository,
)

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "output" / "hwsd.db"


def get_memory_mb() -> float:
    """Return RSS in megabytes."""
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return rss / (1024.0 * 1024.0)


def main() -> None:
    if not DB_PATH.exists():
        print(f"Error: Database missing at {DB_PATH}")
        sys.exit(1)

    repo = SQLiteSoilObservationRepository(DB_PATH)

    # Get distinct SMU IDs
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute(
        "SELECT DISTINCT HWSD2_SMU_ID FROM HWSD2_LAYERS WHERE HWSD2_SMU_ID IS NOT NULL"
    )
    smu_ids = [r[0] for r in cursor.fetchall()]
    conn.close()

    for count in [1, 100, 1000, 10000]:
        random.seed(42)
        queries = [random.choice(smu_ids) for _ in range(count)]

        mem_start = get_memory_mb()
        t_start = time.perf_counter()

        durations = []
        for smu_id in queries:
            t0 = time.perf_counter()
            repo.get_by_key(smu_id)
            t1 = time.perf_counter()
            durations.append((t1 - t0) * 1000.0)

        t_end = time.perf_counter()
        mem_end = get_memory_mb()

        total_time_ms = (t_end - t_start) * 1000.0
        avg_ms = total_time_ms / count

        durations.sort()
        median = statistics.median(durations)
        p95 = durations[int(len(durations) * 0.95)] if count >= 20 else durations[-1]
        p99 = durations[int(len(durations) * 0.99)] if count >= 100 else durations[-1]

        print(f"Benchmark: {count:,} queries")
        print(f"  - Total Time: {total_time_ms:.2f} ms")
        print(f"  - Average: {avg_ms:.3f} ms/query")
        print(f"  - Median: {median:.3f} ms")
        print(f"  - P95: {p95:.3f} ms")
        print(f"  - P99: {p99:.3f} ms")
        print(f"  - Memory growth: {mem_end - mem_start:.2f} MB")


if __name__ == "__main__":
    main()
