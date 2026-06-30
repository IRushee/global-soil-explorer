# Verification Report: Database Generation

## Purpose
Verify the correctness of the conversion from Microsoft Access `HWSD2.mdb` to SQLite, checking row count parity, data types mapping, primary key preservation, foreign key integrity, and scientific sentinel cleaning.

## Dataset Used
*   Original: `data/raw/hwsd/HWSD2.mdb`
*   Generated: `data/output/hwsd.db`

## Methodology
*   Executed database ingestion pipeline converting the 25 MDB tables into SQLite.
*   Ran validations comparing:
    1.  Row count parity across all 25 tables.
    2.  Conversion of negative sentinels (`-9`, `-99`, `-9999`) and non-soil flags (`-1` to `-7`) to SQL `NULL` for physical property columns.
    3.  Integrity check (`PRAGMA integrity_check`) and foreign key validation (`PRAGMA foreign_key_check`).
    4.  Reproducibility check comparing two identical sequential generation runs.

## Results
*   **Table Count**: 25 tables successfully generated.
*   **Row Count Parity**: 100% match. (e.g. `HWSD2_LAYERS` count: 408,835; `HWSD2_SMU` count: 29,538).
*   **NULL Conversions**: `493,428` sentinel values successfully cleaned to SQL `NULL`.
*   **Integrity Check**: `ok` (no corrupt pages).
*   **Foreign Keys**: `HWSD2_LAYERS.HWSD2_SMU_ID` references `HWSD2_SMU.HWSD2_SMU_ID` (verified, no mismatches).
*   **Reproducibility**: Identical counts and logical mappings confirmed.

## Conclusion
*   The generated SQLite database is correct, consistent, and provides efficient index access for the runtime repository.
*   All sentinel values are properly mapped, preserving structural and relational database integrity.
*   No critical gaps were identified for the completed milestones.

## References
*   **Document**: *Harmonized World Soil Database v2.0 User Manual* (FAO/IIASA/ISRIC, 2023)
*   **Section**: Section 2.2 (Soil Attribute Tables) and Section 3.2.1 (Non-soil classes).
*   **Table**: Table 3 (HWSD2_LAYERS table structure and attributes definitions).
*   **Field Descriptions**:
    *   `SAND`, `SILT`, `CLAY`, `COARSE` (Sand, Silt, Clay percentage and Coarse fragments): Mapped as values. Negative flag codes `-1` to `-7` represent non-soil classes where physical grain measurements are not applicable.
    *   `PH_WATER` (pH measured in water): Range bounds 0-14. Negative values represent missing measurements.
    *   `BULK_DENSITY` (Ref bulk density): Units in $g/cm^3$. Negative values represent missing data or non-soil features.
    *   `ORG_CARBON` (Organic Carbon percentage): Negative values represent missing measurements.
    *   `CEC_SOIL` (Cation Exchange Capacity): Units in $cmol_c/kg$.
    *   `AWC` (Available Water Capacity): Units in $mm$.
