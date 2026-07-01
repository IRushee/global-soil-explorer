# Domain Completeness Audit & Coverage Specification

This document presents a complete information audit of the Harmonized World Soil Database (HWSD) v2.0 dataset columns, tracing their flow from raw binary and database structures to the Global Soil Explorer API, identifying gaps, and providing a specification catalog for the frontend.

---

## 1. Field Coverage Matrix

### Table: `HWSD2_LAYERS`

| Column Name | Datatype | Units | Scientific Meaning | Mapping Status | Destination/Justification |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `ID` | TEXT | None | Database internal identifier | `✓ preprocessing only` | System internal key. Bypassed in domain. |
| `HWSD2_SMU_ID` | INTEGER | None | Soil Mapping Unit identifier (v2.0) | `✓ represented as metadata` | Core foreign key. Used in spatial routing. |
| `WISE30s_SMU_ID`| TEXT | None | Soil Mapping Unit identifier (WISE 30s) | `✓ intentionally excluded` | Legacy database reference. |
| `HWSD1_SMU_ID` | INTEGER | None | Soil Mapping Unit identifier (v1.x) | `✓ intentionally excluded` | Legacy database reference. |
| `COVERAGE` | INTEGER | None | Map coverage database source | `✓ represented by lookup` | Resolves map source via `D_COVERAGE`. |
| `SEQUENCE` | INTEGER | None | Sequence order of profile in SMU | `✓ already represented` | Sorted profile tuple ordering. |
| `SHARE` | INTEGER | % | Share of profile inside mapping unit | `✓ already represented` | Maps to `composition_share` (float). |
| `NSC_MU_SOURCE1`| TEXT | None | National Soil Classification (label 1) | `✓ intentionally excluded` | Local classification scheme. |
| `NSC_MU_SOURCE2`| TEXT | None | National Soil Classification (label 2) | `✓ intentionally excluded` | Local classification scheme. |
| `WRB_PHASES` | TEXT | None | Soil unit phase symbols (WRB 2022) | `✓ missing from arch` | Resolves phase modifiers via `D_WRB_PHASES`. |
| `WRB4` | TEXT | None | 4-digit WRB 2022 classification code | `✓ already represented` | Maps to `SoilClassification`. |
| `WRB2` | TEXT | None | 2-digit WRB 2022 classification code | `✓ already represented` | Fallback classification symbol. |
| `FAO90` | TEXT | None | FAO 1990 classification code | `✓ already represented` | Fallback classification symbol. |
| `ROOT_DEPTH` | INTEGER | Code | Rootable soil depth classification | `✓ missing from arch` | Soil depth restriction code. |
| `PHASE1` | INTEGER | Code | Soil phase attribute 1 | `✓ missing from arch` | Phase modifier class (e.g. stony). |
| `PHASE2` | INTEGER | Code | Soil phase attribute 2 | `✓ missing from arch` | Phase modifier class. |
| `ROOTS` | INTEGER | Code | Obstacle to roots (European ESDB) | `✓ missing from arch` | Rooting depth constraints. |
| `IL` | INTEGER | Code | Depth to impermeable layer (ESDB) | `✓ missing from arch` | Hydrologic limitation depth. |
| `SWR` | INTEGER | Code | Soil Water Regime (ESDB) | `✓ missing from arch` | Seasonal moisture classification. |
| `DRAINAGE` | INTEGER | Code | Reference Soil Drainage class | `✓ missing from arch` | Drainage rating (e.g. poorly drained). |
| `AWC` | INTEGER | mm | Available Water Capacity of root depth | `✓ already represented` | Maps to `PropertyType.AVAILABLE_WATER_CAPACITY` |
| `ADD_PROP` | INTEGER | Code | Additional soil properties class | `✓ missing from arch` | Soil physical limiters. |
| `LAYER` | TEXT | None | Depth layer tag (D1 to D7) | `✓ preprocessing only` | Core structural layer grouping key. |
| `TOPDEP` | INTEGER | cm | Layer starting depth boundary | `✓ already represented` | Maps to `SoilLayer.top_depth_cm`. |
| `BOTDEP` | INTEGER | cm | Layer ending depth boundary | `✓ already represented` | Maps to `SoilLayer.bottom_depth_cm`. |
| `COARSE` | INTEGER | % vol | Coarse fragments share | `✓ already represented` | Maps to `PropertyType.COARSE_FRAGMENTS`. |
| `SAND` | INTEGER | % wt | Sand fraction weight share | `✓ already represented` | Maps to `PropertyType.SAND`. |
| `SILT` | INTEGER | % wt | Silt fraction weight share | `✓ already represented` | Maps to `PropertyType.SILT`. |
| `CLAY` | INTEGER | % wt | Clay fraction weight share | `✓ already represented` | Maps to `PropertyType.CLAY`. |
| `TEXTURE_USDA` | INTEGER | Code | USDA texture class code | `✓ represented by lookup` | Resolved to texture class names. |
| `TEXTURE_SOTER`| TEXT | Code | SOTER texture class code | `✓ represented by lookup` | SOTER translation reference. |
| `BULK` | REAL | g/cm3 | Measured Bulk Density | `✓ already represented` | Maps to `PropertyType.BULK_DENSITY`. |
| `REF_BULK` | REAL | g/cm3 | Reference Bulk Density (uncompacted) | `✓ missing from arch` | Uncompacted reference baseline. |
| `ORG_CARBON` | REAL | % wt | Organic Carbon share | `✓ already represented` | Maps to `PropertyType.ORGANIC_CARBON`. |
| `PH_WATER` | REAL | ph | pH measured in water dilution | `✓ already represented` | Maps to `PropertyType.PH_WATER`. |
| `TOTAL_N` | REAL | g/kg | Total Nitrogen share | `✓ missing from arch` | Critical chemical fertilizer nutrient. |
| `CN_RATIO` | REAL | Ratio | Carbon-Nitrogen organic ratio | `✓ missing from arch` | Soil biological decomposition index. |
| `CEC_SOIL` | REAL | cmol/kg | Cation Exchange Capacity (Soil) | `✓ already represented` | Maps to `PropertyType.CATION_EXCHANGE_CAPACITY` |
| `CEC_CLAY` | REAL | cmol/kg | Cation Exchange Capacity (Clay) | `✓ missing from arch` | Clay mineral activity coefficient. |
| `CEC_EFF` | REAL | cmol/kg | Effective Cation Exchange Capacity | `✓ missing from arch` | Actual exchangeable bases at soil pH. |
| `TEB` | REAL | cmol/kg | Total Exchangeable Bases | `✓ missing from arch` | Sum of exchangeable cations. |
| `BSAT` | INTEGER | % | Base Saturation | `✓ already represented` | Maps to `PropertyType.BASE_SATURATION`. |
| `ALUM_SAT` | INTEGER | % | Aluminum saturation index | `✓ missing from arch` | Acid toxicity index. |
| `ESP` | INTEGER | % | Exchangeable Sodium Percentage | `✓ missing from arch` | Sodicity/structural degradation index. |
| `TCARBON_EQ` | REAL | % wt | Total Calcium Carbonate equivalent | `✓ missing from arch` | Liming/calcium concentration. |
| `GYPSUM` | REAL | % wt | Gypsum content share | `✓ missing from arch` | Arid soil gypsum concentration. |
| `ELEC_COND` | REAL | dS/m | Electrical Conductivity | `✓ missing from arch` | Salinity index. |

### Table: `HWSD2_SMU` (SMU-level unique columns only)

| Column Name | Datatype | Units | Scientific Meaning | Mapping Status | Destination/Justification |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `KOPPEN` | TEXT | Code | Koppen-Geiger climate zone | `✓ missing from arch` | Dominant local climate class (D_KOPPEN). |
| `WRB2_CODE` | INTEGER | Code | Dominant Soil Group (WRB + phases) | `✓ missing from arch` | Reference classification group. |

---

## 2. End-to-End Information Flow Audit

Data flows successfully from the raw database to SQLite and is accessible during querying. However, several fields are "blocked" (inaccessible) from the domain objects and REST API due to boundaries in the repository and domain layer:

```
[Raw MDB/BIL] ──> [SQLite DB] ──x [Repository] ──x [Domain Model] ──> [FastAPI REST]
```

### Critical Flow Blockages:
1. **Repository Level**: The `SQLiteSoilObservationRepository` defines `_prop_mappings` to query columns from the layers table. Valid chemical properties present in SQLite (like `TOTAL_N`, `CN_RATIO`, `CEC_CLAY`, `TEB`, `ESP`, `GYPSUM`, `ELEC_COND`) are not listed in this mapping, so they are ignored during database row parsing.
2. **Domain Level**: `SoilObservation`, `SoilProfile`, and `SoilLayer` are rigid dataclasses. Extended land qualities such as climate class (`KOPPEN`), drainage rating (`DRAINAGE`), rooting depth class (`ROOT_DEPTH`), and soil phase modifiers (`PHASE1`, `PHASE2`) have no variables in `SoilProfile` or `SoilLayer`, leaving them unmapped.

---

## 3. Recommended Domain Enhancements

To ensure 100% information coverage, we recommend the following non-breaking enhancements to the domain value objects (to be implemented in a subsequent phase):

### A. Add Hydraulic, Agronomic and Climatic Value Objects
*   **`ClimaticContext`**: Holds Koppen-Geiger climate classification codes and labels (e.g. `Af` $\to$ Tropical rainforest).
*   **`HydrologicProfile`**: Captures drainage class, water regime, and impermeable layer depth.
*   **`AgriculturalLimitation`**: Groups rooting depth class, obstacles to roots, base saturation, and soil phases.

### B. Expand `PropertyType`
Include chemical and physical properties currently missing:
*   `TOTAL_N` (Total Nitrogen, $g/kg$)
*   `CN_RATIO` (C/N ratio)
*   `CEC_CLAY` (CEC of clay fraction, $cmolc/kg$)
*   `GYPSUM` (Gypsum content, %)
*   `ELEC_COND` (Electrical Conductivity, $dS/m$)

---

## 4. Repository & API Exposure Strategy

### Repository Capabilities Expansion
The repository interface should be extended to support:
*   `get_smu_metadata(smu_id: int) -> dict`: Retrieve climate and dominant group attributes directly.
*   `get_dictionary(table_name: str) -> dict[str, str]`: Expose full lookup dictionaries (e.g. mapping codes to text).

### API Strategy (`include` query parameters)
API endpoint `GET /soil` will support an `include` modifier parameter:
*   `/soil?latitude=52.0&longitude=10.0&include=all`
*   **Options**:
    *   `metadata`: Return dataset version, cell index, and resolution.
    *   `dictionaries`: Resolve classification codes to textual definitions inline.
    *   `limitations`: Expose physical obstacles, phases, and rooting limitations.

---

## 5. Future Dataset Compatibility

The core domain architecture is designed to be dataset-independent:
*   `Coordinate` and `SoilObservation` are universal.
*   `SoilLayer` accepts arbitrary depth ranges (`top_depth_cm` to `bottom_depth_cm`), supporting datasets that use different depth intervals (such as SoilGrids' standard intervals: 0-5, 5-15, 15-30, 30-60, 60-100, 100-200 cm).
*   `SoilProperty` uses standard `PropertyType` and `Unit` enums, allowing compatibility with datasets using different units via conversion logic.

---

## 6. Frontend Information Catalog

This catalog outlines every piece of information that can be rendered in the user interface, mapping it back to the database sources and verifying its current availability in the backend API.

### Category A: Geographic & Administrative Context
| UI Field Label | Dataset Column Origin | Scientific Purpose | Current API Availability |
| :--- | :--- | :--- | :--- |
| Latitude | Raster Translation | Geographical reference coordinates. | `✓ Available` |
| Longitude | Raster Translation | Geographical reference coordinates. | `✓ Available` |
| Climate Zone | `HWSD2_SMU.KOPPEN` | Koppen-Geiger climate zone. | `✗ Missing` (Needs SMU lookup) |
| Mapping Unit ID| `HWSD2_SMU_ID` | Spatial soil mapping unit code. | `✗ Excluded` (Internal only) |

### Category B: Taxonomic Classification
| UI Field Label | Dataset Column Origin | Scientific Purpose | Current API Availability |
| :--- | :--- | :--- | :--- |
| Taxonomy Standard | Generated | The standard system (WRB 2022, FAO90). | `✓ Available` |
| Soil Group Code | `WRB4` / `WRB2` / `FAO90` | Taxonomic unit symbol. | `✓ Available` |
| Soil Group Name | Lookup reference | Translated taxonomic description. | `✓ Available` |
| Visual Color | `WRB_Class` (Red/Green/Blue) | Standard color mapping for GIS rendering. | `✗ Missing` (In SQLite only) |

### Category C: Physical Properties (Layer-Specific)
| UI Field Label | Dataset Column Origin | Scientific Purpose | Current API Availability |
| :--- | :--- | :--- | :--- |
| Layer Depth Range| `TOPDEP` - `BOTDEP` | Vertical interval boundaries in cm. | `✓ Available` |
| Sand | `SAND` | Percentage share of sand weight. | `✓ Available` |
| Silt | `SILT` | Percentage share of silt weight. | `✓ Available` |
| Clay | `CLAY` | Percentage share of clay weight. | `✓ Available` |
| Coarse Fragments | `COARSE` | Percentage volume of gravel/stones. | `✓ Available` |
| Bulk Density | `BULK` | Soil compactness ($g/cm^3$). | `✓ Available` |

### Category D: Chemical Properties (Layer-Specific)
| UI Field Label | Dataset Column Origin | Scientific Purpose | Current API Availability |
| :--- | :--- | :--- | :--- |
| pH (Water) | `PH_WATER` | Soil acidity/alkalinity index. | `✓ Available` |
| Organic Carbon | `ORG_CARBON` | Soil organic matter and fertility index. | `✓ Available` |
| Cation Exchange (Soil) | `CEC_SOIL` | Soil nutrient holding capacity ($cmolc/kg$). | `✓ Available` |
| Base Saturation | `BSAT` | Percentage of exchangeable basic cations. | `✓ Available` |
| Total Nitrogen | `TOTAL_N` | Primary macronutrient share. | `✗ Missing` (Needs repo mapping) |
| C/N Ratio | `CN_RATIO` | Decomposition status of organic matter. | `✗ Missing` (Needs repo mapping) |
| Electrical Conductivity | `ELEC_COND` | Soil salinity indicator. | `✗ Missing` (Needs repo mapping) |

### Category E: Hydraulic & Agricultural Limitations (Profile-Specific)
| UI Field Label | Dataset Column Origin | Scientific Purpose | Current API Availability |
| :--- | :--- | :--- | :--- |
| Available Water Capacity| `AWC` | Root-accessible water storage ($mm$). | `✓ Available` (In properties list) |
| Soil Drainage | `DRAINAGE` | Soil wetness/aeration class. | `✗ Missing` (Needs repo mapping) |
| Root Obstacle | `ROOTS` | Physical/chemical depth limitation. | `✗ Missing` (Needs repo mapping) |
| Impermeable Layer | `IL` | Soil depth where water cannot penetrate. | `✗ Missing` (Needs repo mapping) |
| Soil Phase Modifier | `PHASE1` / `PHASE2` | Additional constraints (stony, saline, etc).| `✗ Missing` (Needs repo mapping) |
