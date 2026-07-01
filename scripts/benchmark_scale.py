# ruff: noqa
"""Scale benchmarking script for domain value objects."""

import resource
import time
from backend.domain import *


def get_memory_usage_mb() -> float:
    """Return resident set size in megabytes."""
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return rss / (1024.0 * 1024.0)


def benchmark(n: int) -> None:
    # Clear memory start
    mem_start = get_memory_usage_mb()
    t0 = time.perf_counter()

    objects = []
    for _ in range(n):
        phys = PhysicalProperties(sand=40.0, silt=30.0, clay=30.0, bulk_density=1.4)
        chem = ChemicalProperties(ph=6.5, organic_carbon=2.5)
        hyd = HydraulicProperties(available_water_capacity=150.0)
        measure = LayerMeasurements(physical=phys, chemical=chem, hydraulic=hyd)
        env = EnvironmentalContext(koppen_climate="A")
        hydro = HydrologicContext(drainage="MW")
        limits = LandLimitations(root_depth=1)
        meta = DatasetMetadata(coverage=1, library="HWSD")
        # Keep references to measure memory
        objects.append((phys, chem, hyd, measure, env, hydro, limits, meta))

    t1 = time.perf_counter()
    mem_end = get_memory_usage_mb()

    total_time_ms = (t1 - t0) * 1000.0
    avg_creation_time_us = (total_time_ms * 1000.0) / n
    mem_diff_mb = mem_end - mem_start

    print(f"Scale: {n:,} instances")
    print(f"  - Total Time: {total_time_ms:.2f} ms")
    print(f"  - Avg creation time: {avg_creation_time_us:.3f} microseconds")
    print(f"  - Memory growth: {mem_diff_mb:.2f} MB")


if __name__ == "__main__":
    for count in [10000, 100000, 1000000]:
        benchmark(count)
