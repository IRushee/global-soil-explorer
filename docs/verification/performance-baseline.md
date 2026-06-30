# Verification Report: Performance Baseline

## Purpose
Document baseline performance measurements for offline dataset preprocessing, database generation, runtime repository queries, and spatial raster lookup resolution on specific hardware and software configurations.

## Dataset Used
*   Official HWSD v2.0 raw dataset (`HWSD2.mdb`, `HWSD2.bil`).
*   Generated SQLite database (`hwsd.db`).

## Methodology
*   Offline: Executed the preprocessing conversion pipeline, timing database schema creation, row writing, validation checks, and reproducibility checks.
*   Runtime: Executed 100 E2E repository key lookups for a multi-profile SMU (SMU ID 1666) to separately measure SQLite query execution vs domain mapping and value object reconstruction.
*   Spatial Lookup: Benchmarked the complete E2E lookup resolution (including Coordinate validation, coordinate translation to row/col indices, file lock acquisition, seek/read operations, and decoding) over randomized WGS84 coordinates across multiple scales (1, 100, 1000, and 10000 lookups).

## Results

### 1. Environment Specifications
*   **Hardware**:
    *   **CPU**: Apple M4 (Mac16,12)
    *   **RAM**: 16 GB LPDDR5
    *   **Storage Type**: Apple NVMe SSD
    *   **Operating System**: macOS (Darwin)
*   **Software**:
    *   **Python Version**: 3.11.15
    *   **SQLite Version**: 3.53.1
    *   **Dataset version**: HWSD v2.0

### 2. Measured Execution Times
*   **Tabular Ingest & SQLite Generation**: `14.4 seconds` (includes copying all 25 tables, null calculations, validations, and generating the database twice to prove reproducibility).
*   **Repository SQLite Query Only (average)**: `14.237 ms` (establishing connections, issuing SELECT query, and fetching raw database rows).
*   **Domain mapping & value object reconstruction (average)**: `1.187 ms` (instantiating Coordinate, Observations, Profiles, Layers, Properties, and Classifications).
*   **Total End-to-End Repository Lookup (average)**: `15.424 ms`.

### 3. Spatial Lookup Performance (Pure Python Benchmark)
Latency metrics for resolving coordinate queries on the binary raster grid:

*   **1 Lookup**:
    *   Average: `0.006 ms`
*   **100 Lookups**:
    *   Average: `0.002 ms` | Median: `0.002 ms` | Min: `0.001 ms` | Max: `0.005 ms` | 95th Percentile: `0.002 ms`
*   **1000 Lookups**:
    *   Average: `0.002 ms` | Median: `0.002 ms` | Min: `0.001 ms` | Max: `0.007 ms` | 95th Percentile: `0.002 ms`
*   **10000 Lookups**:
    *   Average: `0.010 ms` | Median: `0.001 ms` | Min: `0.001 ms` | Max: `0.793 ms` | 95th Percentile: `0.103 ms`

## Conclusion
*   Offline database ingestion is extremely fast, executing under 15 seconds.
*   Runtime lookups resolve in under 16 ms, with SQLite query time representing the primary latency component (~92.3%) and domain mapping taking less than 1.2 ms (~7.7%).
*   Spatial lookup is highly optimized, completing individual coordinate resolutions in under 10 microseconds on average.
*   These measurements serve as baselines only. Actual performance depends on target deployment hardware.
