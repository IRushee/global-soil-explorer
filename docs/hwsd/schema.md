# Database Schema Analysis: HWSD v2.0

---

## Document Metadata
*   **Purpose**: Catalog and detail the structural schema for every table and column inside `HWSD2.mdb`.
*   **Audience**: GIS database developers and backend engineers.
*   **Assumptions**:
    *   The schema is mapped from the raw, unmodified Microsoft Access database file.
    *   Interpretation of columns is restricted to structural purposes and officially documented attributes.

---

## 1. Verified Facts
1.  **Core Tables**: The database structures all raw soil attributes in `HWSD2_LAYERS` (48 columns, 408,835 rows) and general mapping unit metadata in `HWSD2_SMU` (23 columns, 29,538 rows).
2.  **Identified Keys**: Both primary tables define `ID` as their primary key and feature an index on the column `HWSD2_SMU_ID`.
3.  **Dictionary Lookup References**: Core variables (such as `COVERAGE`, `WRB4`, `WRB2`, `FAO90`, `PHASE1`, `DRAINAGE`, and `ADD_PROP`) represent code values that correspond directly to the `CODE` primary key inside lookup tables prefixed with `D_`.
4.  **Vertical Intervals**: The `LAYER` column inside `HWSD2_LAYERS` acts as the categorical descriptor dividing data into seven vertical layers: `D1` through `D7`.
5.  **Coordinate Projection**: The raster spatial data maps coordinates directly to `HWSD2_SMU_ID` values.

---

## 2. Reasonable Inferences
1.  **SMU vs. Layers Division**: `HWSD2_SMU` holds general summary data representing the dominant characteristics of the Mapping Unit (such as Koppen-Geiger climate classification). `HWSD2_LAYERS` contains the disaggregated components (`SEQUENCE` of component soils) and their vertical physical/chemical layers (`LAYER` D1 to D7) that make up a single mapping unit.
2.  **Lookup System**: The `D_` tables indicate "Dictionaries" where numeric or short-string keys are translated to clean user-facing labels.
3.  **WRB Tables Purpose**: Tables starting with `WRB_` store reference styling data, labels, and RGB color values for mapping categories under the World Reference Base system.

---

## 3. Unknowns
1.  **Layer Integrity**: It is unknown if there is a strict check constraint enforcing that `LAYER` only contains values between `D1` and `D7`, or if other layers exist.
2.  **Composite Index Definitions**: It is unknown whether the combination of (`HWSD2_SMU_ID`, `SEQUENCE`, `LAYER`) forms a unique index constraint in `HWSD2_LAYERS` to identify individual physical layer rows.
3.  **Calculated Aggregates**: It is unknown if the physical and chemical fields inside `HWSD2_SMU` (such as `BULK_DENSITY` or `AWC`) are derived averages of the depth layers in `HWSD2_LAYERS`, or represent independent topsoil/subsoil predictions.

---

## 4. Core Table Column Catalogs

### Table: `HWSD2_LAYERS`
*   *Purpose*: Primary attribute database storing soil characteristics across 7 depth layers.
*   *Row Count*: 408,835
*   *Column Count*: 48

| Column Name | Data Type | Nullable | Unique (Est) | Example | Possible Meaning | Referenced? |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`ID`** | INTEGER | No | 408,835 | `1` | Database row identifier (Primary Key) | No |
| **`HWSD2_SMU_ID`** | INTEGER | No | ~30,000 | `1666` | Soil Mapping Unit identifier (foreign key link) | Yes (Raster & `HWSD2_SMU`) |
| **`NSC_MU_SOURCE1`**| VARCHAR | Yes | Low | `NULL` | National Soil Classification source string 1 | No |
| **`NSC_MU_SOURCE2`**| VARCHAR | Yes | Low | `NULL` | National Soil Classification source string 2 | No |
| **`WISE30s_SMU_ID`**| VARCHAR | Yes | ~30,000 | `"WD10001666"` | Mapping Unit Key in the WISE30s database | No |
| **`HWSD1_SMU_ID`** | INTEGER | Yes | ~16,000 | `1666` | Mapping Unit Key in the older HWSD v1.2 | No |
| **`COVERAGE`** | INTEGER | Yes | < 10 | `4` | Dataset geographical coverage code | Yes (Maps to `D_COVERAGE`) |
| **`SEQUENCE`** | INTEGER | Yes | < 10 | `1` | Order sequence of soil component in map unit | No |
| **`SHARE`** | INTEGER | Yes | 100 | `70` | Percentage share of this soil type in map unit | No |
| **`NSC`** | VARCHAR | Yes | Low | `NULL` | National Soil Classification code | No |
| **`WRB_PHASES`** | VARCHAR | Yes | ~500 | `"RGeu"` | WRB soil phase classification code | Yes (Maps to `D_WRB_PHASES`) |
| **`WRB4`** | VARCHAR | Yes | ~200 | `"RGeu"` | WRB 4-digit soil classification code | Yes (Maps to `D_WRB4`) |
| **`WRB2`** | VARCHAR | Yes | < 50 | `"RG"` | WRB 2-digit soil classification code | Yes (Maps to `D_WRB2`) |
| **`FAO90`** | VARCHAR | Yes | ~200 | `"RGe"` | Legacy FAO 1990 Soil Classification code | Yes (Maps to `D_FAO90`) |
| **`ROOT_DEPTH`** | INTEGER | Yes | < 10 | `NULL` | Rootable soil depth classification code | Yes (Maps to `D_ROOT_DEPTH`) |
| **`PHASE1`** | INTEGER | Yes | < 50 | `NULL` | Soil physical phase constraint 1 code | Yes (Maps to `D_PHASE`) |
| **`PHASE2`** | INTEGER | Yes | < 50 | `NULL` | Soil physical phase constraint 2 code | Yes (Maps to `D_PHASE`) |
| **`ROOTS`** | INTEGER | Yes | < 10 | `NULL` | Obstruction depth to roots in cm | Yes (Maps to `D_ROOTS`) |
| **`IL`** | INTEGER | Yes | < 10 | `NULL` | Impermeable layer depth in cm | Yes (Maps to `D_IL`) |
| **`SWR`** | INTEGER | Yes | < 10 | `NULL` | Soil water regime code | Yes (Maps to `D_SWR`) |
| **`DRAINAGE`** | VARCHAR | Yes | < 10 | `"MW"` | Reference soil drainage classification code | Yes (Maps to `D_DRAINAGE`) |
| **`AWC`** | INTEGER | Yes | ~200 | `NULL` | Available Water Capacity in mm | No |
| **`ADD_PROP`** | INTEGER | Yes | < 5 | `0` | Additional property constraint code | Yes (Maps to `D_ADD_PROP`) |
| **`LAYER`** | VARCHAR | No | 7 | `"D2"` | Soil layer depth interval category (D1 to D7) | No |
| **`TOPDEP`** | INTEGER | No | 7 | `20` | Depth at top boundary of layer (cm) | No |
| **`BOTDEP`** | INTEGER | No | 7 | `40` | Depth at bottom boundary of layer (cm) | No |
| **`COARSE`** | INTEGER | Yes | 100 | `18` | Percentage volume of coarse fragments | No |
| **`SAND`** | INTEGER | Yes | 100 | `68` | Percentage weight of sand content | No |
| **`SILT`** | INTEGER | Yes | 100 | `18` | Percentage weight of silt content | No |
| **`CLAY`** | INTEGER | Yes | 100 | `14` | Percentage weight of clay content | No |
| **`TEXTURE_USDA`** | INTEGER | Yes | 13 | `11` | Texture class code (USDA standard) | Yes (Maps to `D_TEXTURE_USDA`) |
| **`TEXTURE_SOTER`**| VARCHAR | Yes | 5 | `"C"` | Texture class code (SOTER standard) | Yes (Maps to `D_TEXTURE_SOTER`) |
| **`BULK`** | REAL | Yes | ~100 | `1.45` | Measured bulk density in g/cm3 | No |
| **`REF_BULK`** | REAL | Yes | ~100 | `1.61` | Reference bulk density in g/cm3 | No |
| **`ORG_CARBON`** | REAL | Yes | ~500 | `0.431` | Percentage weight of organic carbon | No |
| **`PH_WATER`** | REAL | Yes | ~100 | `6.4` | Soil pH value measured in water | No |
| **`TOTAL_N`** | REAL | Yes | ~100 | `0.47` | Total nitrogen content in g/kg | No |
| **`CN_RATIO`** | REAL | Yes | ~100 | `10.0` | Carbon/Nitrogen (C/N) ratio | No |
| **`CEC_SOIL`** | INTEGER | Yes | ~150 | `8` | Soil Cation Exchange Capacity in cmolc/kg | No |
| **`CEC_CLAY`** | INTEGER | Yes | ~150 | `50` | Clay Cation Exchange Capacity in cmolc/kg | No |
| **`CEC_EFF`** | REAL | Yes | ~150 | `4.0` | Effective Cation Exchange Capacity in cmolc/kg | No |
| **`TEB`** | REAL | Yes | ~150 | `5.0` | Total Exchangeable Bases in cmolc/kg | No |
| **`BSAT`** | INTEGER | Yes | 100 | `71` | Base saturation percentage | No |
| **`ALUM_SAT`** | INTEGER | Yes | 100 | `0` | Aluminum saturation percentage | No |
| **`ESP`** | INTEGER | Yes | 100 | `4` | Exchangeable Sodium Percentage | No |
| **`TCARBON_EQ`** | REAL | Yes | ~100 | `0.0` | Calcium carbonate equivalent percentage | No |
| **`GYPSUM`** | REAL | Yes | ~100 | `2.9` | Gypsum content percentage by weight | No |
| **`ELEC_COND`** | INTEGER | Yes | ~50 | `1` | Electrical conductivity in dS/m | No |

---

### Table: `HWSD2_SMU`
*   *Purpose*: Mapping Unit metadata table containing dominant soil descriptors.
*   *Row Count*: 29,538
*   *Column Count*: 23

| Column Name | Data Type | Nullable | Unique (Est) | Example | Possible Meaning | Referenced? |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`ID`** | INTEGER | No | 29,538 | `669` | Database row identifier (Primary Key) | No |
| **`HWSD2_SMU_ID`** | INTEGER | No | ~30,000 | `12707` | Soil Mapping Unit identifier (joins to raster/layers)| Yes (Raster & `HWSD2_LAYERS`)|
| **`WISE30s_SMU_ID`**| VARCHAR | Yes | ~30,000 | `"WD10012707"` | Mapping Unit Key in the WISE30s database | No |
| **`HWSD1_SMU_ID`** | INTEGER | Yes | ~16,000 | `12707` | Mapping Unit Key in the older HWSD v1.2 | No |
| **`COVERAGE`** | INTEGER | Yes | < 10 | `3` | Dataset geographical coverage code | Yes (Maps to `D_COVERAGE`) |
| **`SHARE`** | INTEGER | Yes | 100 | `40` | Percentage share of dominant soil component | No |
| **`WRB4`** | VARCHAR | Yes | ~200 | `"ALfr"` | Dominant soil WRB 4-digit code | Yes (Maps to `D_WRB4`) |
| **`WRB_PHASES`** | VARCHAR | Yes | ~500 | `"ALfr"` | Dominant soil WRB phase code | Yes (Maps to `D_WRB_PHASES`) |
| **`WRB2`** | VARCHAR | Yes | < 50 | `"AL"` | Dominant soil WRB 2-digit code | Yes (Maps to `D_WRB2`) |
| **`WRB2_CODE`** | INTEGER | Yes | < 50 | `2` | Dominant soil group classification code | Yes (Maps to `D_WRB2code`) |
| **`FAO90`** | VARCHAR | Yes | ~200 | `"ALf"` | Dominant soil legacy FAO 1990 code | Yes (Maps to `D_FAO90`) |
| **`KOPPEN`** | VARCHAR | Yes | < 50 | `"A"` | Koppen-Geiger climate classification | Yes (Maps to `D_KOPPEN`) |
| **`TEXTURE_USDA`** | INTEGER | Yes | 13 | `11` | Dominant soil topsoil texture class | Yes (Maps to `D_TEXTURE_USDA`) |
| **`REF_BULK_DENSITY`**| REAL | Yes | ~100 | `1.63` | Reference bulk density of dominant soil (g/cm3) | No |
| **`BULK_DENSITY`** | REAL | Yes | ~100 | `1.35` | Measured bulk density of dominant soil (g/cm3) | No |
| **`DRAINAGE`** | VARCHAR | Yes | < 10 | `"MW"` | Dominant soil reference drainage class code | Yes (Maps to `D_DRAINAGE`) |
| **`ROOT_DEPTH`** | INTEGER | Yes | < 10 | `1` | Dominant soil rooting depth code | Yes (Maps to `D_ROOT_DEPTH`) |
| **`AWC`** | INTEGER | Yes | ~200 | `168` | Available Water Capacity in mm/m | No |
| **`PHASE1`** | INTEGER | Yes | < 50 | `NULL` | Dominant soil physical phase constraint 1 | Yes (Maps to `D_PHASE`) |
| **`PHASE2`** | INTEGER | Yes | < 50 | `NULL` | Dominant soil physical phase constraint 2 | Yes (Maps to `D_PHASE`) |
| **`ROOTS`** | INTEGER | Yes | < 10 | `NULL` | Obstruction depth to roots (dominant soil) | Yes (Maps to `D_ROOTS`) |
| **`IL`** | INTEGER | Yes | < 10 | `NULL` | Impermeable layer depth (dominant soil) | Yes (Maps to `D_IL`) |
| **`ADD_PROP`** | INTEGER | Yes | < 5 | `0` | Additional property constraint (dominant soil) | Yes (Maps to `D_ADD_PROP`) |

---

## 5. Metadata and Dictionary Tables Schema

### Dictionary Tables (`D_*`)
The 18 dictionary lookup tables share a uniform structure:
*   **`CODE`** (or **`SYMBOL`** / **`ID`**): `INTEGER` or `VARCHAR`, Primary Key. Serves as the index referenced by core tables.
*   **`VALUE`**: `VARCHAR`, Nullable. Contains the readable string label.

### Metadata Tables (`HWSD2_*_METADATA`)
The 2 metadata tables share a uniform structure describing variables:
*   **`ID`**: `INTEGER` / `REAL`, Primary Key.
*   **`FIELD`**: `VARCHAR`. Name of the matching column in the core tables.
*   **`UNIT`**: `VARCHAR`. Scientific unit of measure.
*   **`DESCRIPTION`**: `VARCHAR`. Human-readable description of the variable.
*   **`DATATYPE`**: `VARCHAR`. Column format.
*   **`DOMAIN`**: `VARCHAR`. Relational link to the target dictionary lookup table.

### World Reference Base (WRB) Tables

#### Table: `WRB_Class`
*   *Row Count*: 34, *Column Count*: 9
*   *Columns*: `ID` (INTEGER, PK), `ID_Class` (INTEGER, Index), `ClassNumber` (INTEGER), `Divider` (REAL), `Label` (VARCHAR), `Symbol` (VARCHAR), `Red` (INTEGER), `Green` (INTEGER), `Blue` (INTEGER).

#### Table: `WRB_Layer`
*   *Row Count*: 1, *Column Count*: 10
*   *Columns*: `ID` (INTEGER, PK), `ID_AezLibrary` (INTEGER, Index), `LayerName` (VARCHAR), `Filename` (VARCHAR), `Units` (VARCHAR), `Bytes` (INTEGER), `Multiplier` (INTEGER), `ZeroIsValue` (INTEGER), `ID_Class_Type` (INTEGER, Index), `ID_Class` (INTEGER, Index).

#### Table: `WRB_Library`
*   *Row Count*: 1, *Column Count*: 3
*   *Columns*: `ID_AezLibrary` (INTEGER, PK), `AezLibrary` (VARCHAR), `FileName` (VARCHAR).

---

## 6. Key Candidates and Columns Under Investigation

### Candidate Primary Keys
*   **`HWSD2_LAYERS.ID`**: Confirmed as the unique primary key for the soil layers table.
*   **`HWSD2_SMU.ID`**: Confirmed as the unique primary key for the mapping unit catalog.
*   **`D_*.CODE`** (or `SYMBOL`/`ID`): Confirmed primary lookup keys for dictionary translation.

### Candidate Foreign Keys
*   **`HWSD2_LAYERS.HWSD2_SMU_ID`** $\rightarrow$ references **`HWSD2_SMU.HWSD2_SMU_ID`**: Links component soil depth layers back to mapping unit groups.
*   **`WRB_Layer.ID_AezLibrary`** $\rightarrow$ references **`WRB_Library.ID_AezLibrary`**: Relational join for the WRB dataset catalogs.
*   **Core Table Columns (`COVERAGE`, `WRB4`, `DRAINAGE`, etc.)** $\rightarrow$ reference **`D_*.CODE`**: Links database code attributes to readable lookup labels.

### Columns Requiring Further Investigation
*   **`HWSD2_LAYERS.SEQUENCE`**: Needs verification to confirm if this column represents component soil fractions within a single mapping unit.
*   **`HWSD2_LAYERS.NSC`**: Found in actual database column headers but completely omitted from `HWSD2_LAYERS_METADATA`. Needs schema auditing.
*   **`D_WRB2` vs `D_WRB2code`**: Two dictionary tables containing nearly identical lists. We need to identify if one is redundant.
*   **`WRB_Layer` and `WRB_Library`**: Contain only 1 row each. Need to investigate if they serve any practical function in the web GIS system or are relic files.
