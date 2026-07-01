# HWSD v2.0 Known Dataset Anomalies

This document logs all identified anomalies, irregularities, and sentinel placeholder values in the official Harmonized World Soil Database (HWSD) v2.0 dataset, explaining their scientific meaning and how the Global Soil Explorer architecture resolves them.

---

## 1. Additional Property Code 1 Missing Lookup Entry

*   **Affected Tables**: `HWSD2_LAYERS`, `HWSD2_SMU`
*   **Observed Values**: `ADD_PROP = 1`
*   **Expected Values**: `1` should be defined in lookup table `D_ADD_PROP`.
*   **Lookup Contents in `D_ADD_PROP`**:
    *   `0`: "None"
    *   `2`: "Gelic"
    *   `3`: "Vertic"
    *(Code 1 is completely absent).*
*   **Scientific Interpretation**: Code `1` was used during raw compilation to flag specific profile properties (such as legacy salinity or sodicity modifiers from regional records), but the reference table `D_ADD_PROP` was compiled without it.
*   **Impact**: If the domain validator strictly enforces that the value must exist in the lookup set `{0, 2, 3}`, any observation containing `ADD_PROP = 1` fails constructor validation, causing a crash.
*   **Resolution Adopted**: We expanded the `LandLimitations` validation code list to `{0, 1, 2, 3}`. When the repository translates code `1`, it is mapped to a placeholder description `"Unknown / Inconsistent modifier (1)"`, permitting clean model instantiation without data rejection.

---

## 2. SOTER Texture Null Sentinel "-"

*   **Affected Table**: `HWSD2_LAYERS`
*   **Observed Values**: `TEXTURE_SOTER = "-"` or `TEXTURE_SOTER = " - "`
*   **Expected Values**: A database `NULL` or empty string `""` to indicate missing SOTER texture classifications.
*   **Scientific Interpretation**: SOTER classification was not defined for all soil mapping units. Compilers used a literal hyphen string (`"-"`) as a sentinel marker for missing data.
*   **Impact**: The domain validator expects one of the valid SOTER texture symbols: `{'C', 'F', 'M', 'V', 'Z'}`. Passing the hyphen string triggers an `InvalidSoilTextureError`.
*   **Resolution Adopted**: The `SoilTexture` constructor checks if the stripped string is `"-"`. If so, it automatically maps the attribute to `None`, satisfying constructor stability.

---

## 3. Negative Sentinel Values (-9 / -9.0)

*   **Affected Table**: `HWSD2_LAYERS`
*   **Observed Values**: `-9` (integers) or `-9.0` (floats) across physical and chemical property columns (e.g. `SAND`, `CLAY`, `PH_WATER`, `AWC`).
*   **Expected Values**: `NULL` or empty cells.
*   **Scientific Interpretation**: In GIS raster grids and legacy database tables, negative constants (like `-9`, `-99`, `-9999`) are standard sentinels denoting missing observations (No Data).
*   **Impact**: Enforcing scientific boundaries (like sand percentage $[0.0, 100.0]$ or bulk density $>0.0$) throws validation errors if negative sentinels are passed.
*   **Resolution Adopted**: The repository layer filters out `-9` and `-9.0` values, mapping them to Python `None` during query extraction.

---

## 4. Inconsistent NULL Formats

*   **Affected Tables**: All tables in the HWSD dataset.
*   **Observed Values**: Empty strings `""`, spaces `" "`, numeric `-9`, and actual database `NULL` types.
*   **Scientific Interpretation**: HWSD v2.0 is a harmonized compilation of regional soil databases (WISE, ESDB, FAO-UNESCO, SOTER). Different source systems utilized differing conventions to express missing values.
*   **Impact**: Inconsistent parsing and validation logic if not standardized.
*   **Resolution Adopted**: We implement a uniform null filter in the database query parser. Whitespace-only strings, empty strings, and negative numeric sentinels are converted to Python `None` before domain instantiation.
