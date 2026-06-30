# Spatial Lookup Workflow: HWSD v2.0

---

## Document Metadata
*   **Purpose**: Document the step-by-step data flow to resolve a user's geographical coordinate query to a complete, interpreted soil profile.
*   **Audience**: Backend developers, database engineers, and UX/UI designers.
*   **Assumptions**:
    *   The `HWSD2.bil` raster file is read as a raw binary stream.
    *   The relational database tables have been successfully migrated to an active SQLite instance.

---

## 1. End-to-End Workflow Steps

### Step 1: Input Coordinates (Lat/Lon)
*   **Verified Workflow**: The user enters or clicks a location on the map, sending latitude and longitude coordinates. The backend checks `HWSD2.prj` to confirm the Coordinate Reference System is WGS 84.
*   **Inputs**: Latitude ($Lat \in [-90, 90]$), Longitude ($Lon \in [-180, 180]$) in decimal degrees.
*   **Outputs**: Validated GPS coordinate pair.
*   **Participating Files**: `HWSD2.prj`
*   **Participating Tables**: None.

### Step 2: Raster Cell Identification (Index Conversion)
*   **Verified Workflow**: The backend uses spatial boundaries and resolution markers defined in `HWSD2.hdr` to calculate the exact row ($r$) and column ($c$) coordinates of the target cell in the $21,600 \times 43,200$ raster grid.
*   **Inputs**: Validated Lat/Lon coordinate pair.
*   **Outputs**: Grid row index ($r \in [0, 21599]$), column index ($c \in [0, 43199]$).
*   **Participating Files**: `HWSD2.hdr`
*   **Participating Tables**: None.
*   **Mathematical Formula**:
    $$c = \lfloor \frac{Lon - ULXMAP}{XDIM} \rfloor$$
    $$r = \lfloor \frac{ULYMAP - Lat}{YDIM} \rfloor$$
    *(where $ULXMAP = -179.995833333333$, $ULYMAP = 89.9958333333333$, $XDIM = YDIM = 0.00833333333333333$)*

### Step 3: Raster Value Extraction
*   **Verified Workflow**: The binary parser opens a file handle to `HWSD2.bil`, seeks to the computed byte offset, and extracts the 16-bit integer cell value (representing the Map Unit Key).
*   **Inputs**: Row index ($r$) and column index ($c$).
*   **Outputs**: 16-bit Unsigned Integer pixel value (Map Unit Key).
*   **Participating Files**: `HWSD2.bil`, `HWSD2.hdr` (used to determine `NBITS`, `BYTEORDER`, and `NODATA` values).
*   **Participating Tables**: None.
*   **Mathematical Formula**:
    $$Offset = (r \times 43200 + c) \times 2 \text{ bytes}$$
    *If the extracted value equals the `NODATA` marker (65535), the workflow terminates and returns an empty soil profile (representing water or unmapped land).*

### Step 4: Mapping to `HWSD2_SMU_ID`
*   **Verified Workflow**: The extracted 16-bit pixel integer is assigned directly as the primary relational query parameter `HWSD2_SMU_ID`.
*   **Inputs**: 16-bit Integer pixel value.
*   **Outputs**: Relational Query Key (`HWSD2_SMU_ID`).
*   **Participating Files**: None (handled in application memory).
*   **Participating Tables**: None.

### Step 5: Database Lookup (SMU Metadata)
*   **Verified Workflow**: The system queries the `HWSD2_SMU` table to retrieve general descriptors for the Soil Mapping Unit (such as Koppen-Geiger climate classification, dominant soil symbol, and overall drainage properties).
*   **Inputs**: `HWSD2_SMU_ID`.
*   **Outputs**: General Soil Mapping Unit database record.
*   **Participating Files**: `HWSD2.sqlite`
*   **Participating Tables**: `HWSD2_SMU`

### Step 6: Layer & Component Soil Retrieval
*   **Verified Workflow**: The system queries `HWSD2_LAYERS` to pull all soil components and vertical layers associated with the `HWSD2_SMU_ID`. Records are ordered by component sequence and layer depth.
*   **Inputs**: `HWSD2_SMU_ID`.
*   **Outputs**: Array of raw database records containing layer bounds (`TOPDEP`, `BOTDEP`) and soil physical/chemical parameters for all 7 layers (`D1`–`D7`).
*   **Participating Files**: `HWSD2.sqlite`
*   **Participating Tables**: `HWSD2_LAYERS`

### Step 7: Lookup Table (Dictionary) Resolution
*   **Verified Workflow**: Code variables in the retrieved records (like texture codes, drainage classes, and phase codes) are resolved against standard lookup dictionaries to obtain human-readable labels.
*   **Inputs**: Array of raw integers and code abbreviations.
*   **Outputs**: Resolved, readable text strings.
*   **Participating Files**: `HWSD2.sqlite`
*   **Participating Tables**: `D_COVERAGE`, `D_WRB4`, `D_WRB2`, `D_FAO90`, `D_DRAINAGE`, `D_ROOT_DEPTH`, `D_PHASE`, `D_ROOTS`, `D_IL`, `D_TEXTURE_USDA`, `D_TEXTURE_SOTER`, `D_ADD_PROP`, `D_SWR`, `D_WRB2code`.

### Step 8: Final Interpreted Soil Profile
*   **Inferred Workflow**: The application joins the general SMU characteristics with the ordered component soil records. For each component, it stacks the 7 depth layers vertically to generate a complete visual soil profile payload returned as a structured JSON object to the UI.
*   **Inputs**: Merged attributes and dictionary-resolved labels.
*   **Outputs**: Standardized JSON Soil Profile payload.
*   **Participating Files**: None.
*   **Participating Tables**: None.

---

## 2. Workflow Classification

### Verified Workflow
*   The math converting geographic coordinates to index row/column offsets in the $21,600 \times 43,200$ grid.
*   Seeks and reads in raw `HWSD2.bil` using a binary byte offset.
*   Performing SQL queries on `HWSD2_SMU` and `HWSD2_LAYERS` using the index value `HWSD2_SMU_ID`.
*   Resolving integer codes using `CODE` joins against `D_*` lookup tables.

### Inferred Workflow
*   Handling multiple soil components within a single Mapping Unit. We infer that `SEQUENCE` identifies separate soils sharing the unit, and the percentage `SHARE` represents their spatial fraction. The application must render these as parallel profile options for the same coordinate.
*   We infer that `LAYER` values `D1` through `D7` represent static vertical segments (0–20, 20–40, 40–60, 60–80, 80–100, 100–150, 150–200 cm).

### Unknown Workflow
*   How does the spatial seek handle pixel boundary offsets? We need to validate if the coordinate point matches the center of the pixel or if edge alignments require correction.
*   How should the workflow handle coordinate queries that yield valid mapping units but contain completely empty (`NULL`) properties inside `HWSD2_LAYERS`?

---

## 3. Assumptions & Validation Questions

### Known Assumptions
1.  **Coordinate Reference System**: Coordinates entered on the client side use the WGS 84 datum. Any projection conversion (e.g. from Web Mercator) must occur in the client interface before requesting lookups from the spatial backend.
2.  **NoData Value**: An extracted pixel value of `65535` is assumed to represent water/unmapped territory, halting subsequent database queries immediately to save resources.

### Unknowns Requiring Validation
1.  **Pixel Edge Alignment**: Does the calculated column/row index require a half-pixel adjustment (e.g., `-0.5` cell dimensions) to correctly align with standard GIS pixel-center conventions?
2.  **Referential Integrity Constraints**: Are there any scenarios where `HWSD2_SMU_ID` is found in the spatial raster but yields zero records in `HWSD2_SMU` or `HWSD2_LAYERS`?
3.  **Missing Dictionary Keys**: Are there integer codes mapped in the core tables that are missing from their respective dictionary (`D_*`) lookup tables, causing join failures?
