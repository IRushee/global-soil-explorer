# Verification Report: Domain Validation

## Purpose
Verify the compliance of the offline/runtime domain model value objects against real dataset values, ensuring that invariants are correctly enforced.

## Dataset Used
*   Official HWSD v2.0 raw dataset (specifically `HWSD2.mdb` data records).

## Methodology
*   Loaded and instantiated all `HWSD2_LAYERS` (408,835 layers) and `HWSD2_SMU` (29,538 components) into domain representations:
    *   `Coordinate`
    *   `SoilProperty`
    *   `SoilClassification`
    *   `SoilLayer`
    *   `SoilProfile`
    *   `SoilObservation`
*   Verified that:
    1.  No type constraints or float invariants are violated.
    2.  Negative placeholders in properties (non-soil categories `-1` to `-7`) are cleanly mapped to `NULL` / omitted instead of raising range exceptions.
    3.  WRB 2022, WRB 2nd Edition, and FAO 90 codes are successfully matched to dictionary lookups.

## Results
*   **Layer Stacking**: Top and bottom depths are verified. `top_depth_cm <= bottom_depth_cm` was validated for all 408,835 records.
*   **Soil Properties**: Range constraints (e.g. pH within 0-14, fractions within 0-100%) successfully accommodated every valid scientific record.
*   **Sentinels**: Missing data and flags were properly parsed, avoiding invariant validation failures.

## Conclusion
*   The domain model represents the real physical/chemical parameters of the HWSD dataset.
*   All domain invariants are structurally sound and verified.
*   No critical gaps were identified for the completed milestones.

## References
*   *Harmonized World Soil Database v2.0 User Manual*, Section 2.1 (Structure of the Database) and Section 2.2 (Soil Attribute Tables).
