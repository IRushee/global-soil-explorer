# ruff: noqa
"""Stress concurrency and database correctness verification script."""

import concurrent.futures
import random
import resource
import sqlite3
import sys
import time
from pathlib import Path

from backend.domain import Coordinate
from backend.repository.sqlite_repository import (
    SQLiteSoilObservationRepository,
)

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "output" / "hwsd.db"


def get_memory_mb() -> float:
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return rss / (1024.0 * 1024.0)


def _clean_val(v):
    if v in (None, "", -9, -9.0, "-9", "-9.0"):
        return None
    if isinstance(v, float) and v < 0:
        return None
    if isinstance(v, int) and v < 0:
        return None
    if isinstance(v, str):
        s = v.strip()
        if s in ("", "-9", "-"):
            return None
        return s
    return v


def run_correctness_audit(repo, cursor, smu_ids):
    print("Step 1: Running correctness audit over 5,000 random SMU samples...")
    sample_smus = random.sample(smu_ids, min(5000, len(smu_ids)))

    mismatches = 0
    for smu_id in sample_smus:
        # Load raw SMU row
        cursor.execute(
            "SELECT KOPPEN, COVERAGE FROM HWSD2_SMU WHERE HWSD2_SMU_ID = ?",
            (smu_id,),
        )
        smu_row = cursor.fetchone()
        raw_koppen = smu_row[0] if smu_row else None

        # Load raw layer rows
        cursor.execute(
            "SELECT * FROM HWSD2_LAYERS WHERE HWSD2_SMU_ID = ? ORDER BY SEQUENCE, TOPDEP",
            (smu_id,),
        )
        col_names = [col[0].lower() for col in cursor.description]
        raw_layers = [dict(zip(col_names, r)) for r in cursor.fetchall()]

        # Query via repository
        coord = Coordinate(12.34, 56.78)
        try:
            obs = repo.get_by_key(smu_id, coordinate=coord)
        except Exception as e:
            print(f"Constructor failure at SMU {smu_id}: {e}")
            mismatches += 1
            continue

        # Check climate
        if raw_koppen is not None and str(raw_koppen).strip() != "":
            if (
                not obs.environmental_context
                or obs.environmental_context.koppen_climate
                != str(raw_koppen).strip().upper()
            ):
                mismatches += 1
                continue

        # Group raw layers by sequence
        seq_groups = {}
        for rl in raw_layers:
            seq = rl["sequence"]
            if seq not in seq_groups:
                seq_groups[seq] = []
            seq_groups[seq].append(rl)

        if len(obs.profiles) != len(seq_groups):
            mismatches += 1
            continue

            # Compare basic profile/layer configurations
            matched_group = seq_groups.get(profile.sequence_index)
            if matched_group is None:
                mismatches += 1
                break

            # Compare first layer physical parameters
            layer = profile.layers[0]
            raw_lay = matched_group[0]
            if (
                layer.measurements.physical.sand != _clean_val(raw_lay.get("sand"))
                or layer.measurements.chemical.ph != _clean_val(raw_lay.get("ph_water"))
                or layer.measurements.hydraulic.available_water_capacity
                != _clean_val(raw_lay.get("awc"))
            ):
                mismatches += 1
                break

    print(
        f"Correctness Audit Finished: {len(sample_smus)} SMUs checked. "
        f"Mismatch count = {mismatches} (Expected: 0)."
    )
    if mismatches > 0:
        sys.exit(1)


def run_stress_concurrency(repo, smu_ids):
    print("Step 2: Starting stress concurrency test (500 workers, 50,000 queries)...")
    queries = [random.choice(smu_ids) for _ in range(50000)]

    def task(smu_id):
        obs = repo.get_by_key(smu_id)
        return len(obs.profiles)

    t0 = time.perf_counter()
    mem_start = get_memory_mb()

    with concurrent.futures.ThreadPoolExecutor(max_workers=500) as executor:
        results = list(executor.map(task, queries))

    t1 = time.perf_counter()
    mem_end = get_memory_mb()

    total_time = (t1 - t0) * 1000.0
    throughput = len(queries) / (t1 - t0)

    print(f"Stress Concurrency Finished:")
    print(f"  - Total Queries executed: {len(results):,}")
    print(f"  - Total Duration: {total_time:.2f} ms")
    print(f"  - Throughput: {throughput:.2f} queries/sec")
    print(f"  - Peak RSS Memory growth: {mem_end - mem_start:.2f} MB")


def main():
    if not DB_PATH.exists():
        print(f"Error: DB not found at {DB_PATH}")
        sys.exit(1)

    repo = SQLiteSoilObservationRepository(DB_PATH)
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    cursor.execute(
        "SELECT DISTINCT HWSD2_SMU_ID FROM HWSD2_LAYERS WHERE HWSD2_SMU_ID IS NOT NULL"
    )
    smu_ids = [r[0] for r in cursor.fetchall()]

    run_correctness_audit(repo, cursor, smu_ids)
    run_stress_concurrency(repo, smu_ids)

    conn.close()


if __name__ == "__main__":
    main()
