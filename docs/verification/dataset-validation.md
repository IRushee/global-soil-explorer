# Verification Report: Dataset Validation

## Purpose
Verify the existence, readability, and consistency of the raw HWSD v2.0 dataset files, ensuring that header metadata matches the physical binary grid dimensions.

## Dataset Used
*   Official HWSD v2.0 raw dataset located at `data/raw/hwsd/` comprising:
    *   `HWSD2.bil` (flat binary spatial grid)
    *   `HWSD2.hdr` (ENVI header file)
    *   `HWSD2.prj` (Coordinate Reference System definition)
    *   `HWSD2.mdb` (Microsoft Access relational database)

## Methodology
*   Independent code-level checks verifying that:
    1.  The `.bil` file is present and its size matches the formula: `NCOLS (43200) * NROWS (21600) * (NBITS (16) / 8) = 1,866,240,000 bytes`.
    2.  Header variables (`ncols`, `nrows`, `nbits`, `pixeltype`, `xdim`, `ydim`, `ulxmap`, `ulymap`) are parsed correctly.
    3.  Projection variables map to standard EPSG:4326/WGS84.
    4.  No duplicate files exist, and all paths are readable.

## Results
*   Header Metadata:
    *   `ncols`: 43,200
    *   `nrows`: 21,600
    *   `nbits`: 16 (Signed 16-bit integer, PIXELTYPE=SIGNEDINT)
    *   `ulxmap`: -179.995833333333
    *   `ulymap`: 89.9958333333333
    *   `xdim`: 0.00833333333333333 (30 arc-seconds)
    *   `ydim`: 0.00833333333333333
*   File Size Check: Expected `1,866,240,000` bytes; Actual size matches exactly.
*   MDB File: Discovered and confirmed readable.

## Conclusion
*   The raw HWSD v2.0 dataset conforms to ENVI flat binary specifications.
*   All file coordinates and grid bounds are correct and ready for lookup.

## References
*   *Harmonized World Soil Database v2.0 User Manual*, Food and Agriculture Organization of the United Nations (FAO), International Institute for Applied Systems Analysis (IIASA), ISRIC-World Soil Information.
