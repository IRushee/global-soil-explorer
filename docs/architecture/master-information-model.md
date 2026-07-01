# Master Information Model Specification

This specification defines the complete information model of the Harmonized World Soil Database (HWSD) v2.0, conceptually flattening the normalized relational database schema into a single unified logical observation record.

---

## 1. Master Schema Inventory

The official HWSD v2.0 dataset comprises 25 tables in total:
*   **Physical Core Tables (2)**: `HWSD2_LAYERS` and `HWSD2_SMU`
*   **Metadata Tables (2)**: `HWSD2_LAYERS_METADATA` and `HWSD2_SMU_METADATA`
*   **Reference/Visualization Tables (3)**: `WRB_Class`, `WRB_Layer`, and `WRB_Library`
*   **Lookup Dictionary Tables (18)**: Tables starting with `D_` prefixes.

### Column Inventory of Core Tables
Below is the complete column inventory for the core physical tables (`HWSD2_LAYERS` and `HWSD2_SMU`), detailing their data type, units, nullability, sentinel values, and scientific meaning:

| Table | Column Name | Datatype | Units | Nullable | Sentinel Values | Lookup Reference | Scientific Meaning |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `HWSD2_LAYERS` | `ID` | TEXT | None | No | None | None | Database internal key |
| `HWSD2_LAYERS` | `HWSD2_SMU_ID` | INTEGER | None | No | None | None | Soil Mapping Unit identifier (v2.0) |
| `HWSD2_LAYERS` | `NSC_MU_SOURCE1`| TEXT | None | Yes | None | None | National Soil Classification symbol 1 |
| `HWSD2_LAYERS` | `NSC_MU_SOURCE2`| TEXT | None | Yes | None | None | National Soil Classification symbol 2 |
| `HWSD2_LAYERS` | `WISE30s_SMU_ID`| TEXT | None | Yes | None | None | Soil Mapping Unit identifier (WISE 30s) |
| `HWSD2_LAYERS` | `HWSD1_SMU_ID` | INTEGER | None | Yes | None | None | Soil Mapping Unit identifier (v1.x) |
| `HWSD2_LAYERS` | `COVERAGE` | INTEGER | None | Yes | None | `D_COVERAGE` | Map coverage database source |
| `HWSD2_LAYERS` | `SEQUENCE` | INTEGER | None | No | None | None | Sequence order of profile in SMU |
| `HWSD2_LAYERS` | `SHARE` | INTEGER | % | No | None | None | Share of profile inside mapping unit |
| `HWSD2_LAYERS` | `NSC` | TEXT | None | Yes | None | None | National Soil Classification code |
| `HWSD2_LAYERS` | `WRB_PHASES` | TEXT | None | Yes | None | `D_WRB_PHASES`| Soil unit phase symbols (WRB 2022) |
| `HWSD2_LAYERS` | `WRB4` | TEXT | None | Yes | None | `D_WRB4` | 4-digit WRB 2022 classification code |
| `HWSD2_LAYERS` | `WRB2` | TEXT | None | Yes | None | `D_WRB2` | 2-digit WRB 2022 classification code |
| `HWSD2_LAYERS` | `FAO90` | TEXT | None | Yes | None | `D_FAO90` | FAO 1990 classification code |
| `HWSD2_LAYERS` | `ROOT_DEPTH` | INTEGER | Code | Yes | -9 | `D_ROOT_DEPTH`| Rootable soil depth classification |
| `HWSD2_LAYERS` | `PHASE1` | INTEGER | Code | Yes | -9 | `D_PHASE` | Soil phase attribute 1 |
| `HWSD2_LAYERS` | `PHASE2` | INTEGER | Code | Yes | -9 | `D_PHASE` | Soil phase attribute 2 |
| `HWSD2_LAYERS` | `ROOTS` | INTEGER | Code | Yes | -9 | `D_ROOTS` | Obstacle to roots (European ESDB) |
| `HWSD2_LAYERS` | `IL` | INTEGER | Code | Yes | -9 | `D_IL` | Depth to impermeable layer (ESDB) |
| `HWSD2_LAYERS` | `SWR` | INTEGER | Code | Yes | -9 | `D_SWR` | Soil Water Regime (ESDB) |
| `HWSD2_LAYERS` | `DRAINAGE` | TEXT | Code | Yes | None | `D_DRAINAGE` | Reference Soil Drainage class |
| `HWSD2_LAYERS` | `AWC` | INTEGER | mm | Yes | -9 | `D_AWC` | AWC of rootable soil depth |
| `HWSD2_LAYERS` | `ADD_PROP` | INTEGER | Code | Yes | -9 | `D_ADD_PROP` | Additional soil properties class |
| `HWSD2_LAYERS` | `LAYER` | TEXT | None | No | None | None | Depth layer tag (D1 to D7) |
| `HWSD2_LAYERS` | `TOPDEP` | INTEGER | cm | No | None | None | Layer starting depth boundary |
| `HWSD2_LAYERS` | `BOTDEP` | INTEGER | cm | No | None | None | Layer ending depth boundary |
| `HWSD2_LAYERS` | `COARSE` | INTEGER | % vol | Yes | -9 | None | Coarse fragments share |
| `HWSD2_LAYERS` | `SAND` | INTEGER | % wt | Yes | -9 | None | Sand fraction weight share |
| `HWSD2_LAYERS` | `SILT` | INTEGER | % wt | Yes | -9 | None | Silt fraction weight share |
| `HWSD2_LAYERS` | `CLAY` | INTEGER | % wt | Yes | -9 | None | Clay fraction weight share |
| `HWSD2_LAYERS` | `TEXTURE_USDA` | INTEGER | Code | Yes | -9 | `D_TEXTURE_USDA`| USDA texture class code |
| `HWSD2_LAYERS` | `TEXTURE_SOTER`| TEXT | Code | Yes | None | `D_TEXTURE_SOTER`| SOTER texture class code |
| `HWSD2_LAYERS` | `BULK` | REAL | g/cm3 | Yes | -9.0 | None | Measured Bulk Density |
| `HWSD2_LAYERS` | `REF_BULK` | REAL | g/cm3 | Yes | -9.0 | None | Reference Bulk Density (uncompacted) |
| `HWSD2_LAYERS` | `ORG_CARBON` | REAL | % wt | Yes | -9.0 | None | Organic Carbon share |
| `HWSD2_LAYERS` | `PH_WATER` | REAL | ph | Yes | -9.0 | None | pH measured in water dilution |
| `HWSD2_LAYERS` | `TOTAL_N` | REAL | g/kg | Yes | -9.0 | None | Total Nitrogen share |
| `HWSD2_LAYERS` | `CN_RATIO` | REAL | Ratio | Yes | -9.0 | None | Carbon-Nitrogen organic ratio |
| `HWSD2_LAYERS` | `CEC_SOIL` | REAL | cmol/kg| Yes | -9.0 | None | Cation Exchange Capacity (Soil) |
| `HWSD2_LAYERS` | `CEC_CLAY` | REAL | cmol/kg| Yes | -9.0 | None | Cation Exchange Capacity (Clay) |
| `HWSD2_LAYERS` | `CEC_EFF` | REAL | cmol/kg| Yes | -9.0 | None | Effective Cation Exchange Capacity |
| `HWSD2_LAYERS` | `TEB` | REAL | cmol/kg| Yes | -9.0 | None | Total Exchangeable Bases |
| `HWSD2_LAYERS` | `BSAT` | INTEGER | % | Yes | -9 | None | Base Saturation |
| `HWSD2_LAYERS` | `ALUM_SAT` | INTEGER | % | Yes | -9 | None | Aluminum saturation index |
| `HWSD2_LAYERS` | `ESP` | INTEGER | % | Yes | -9 | None | Exchangeable Sodium Percentage |
| `HWSD2_LAYERS` | `TCARBON_EQ` | REAL | % wt | Yes | -9.0 | None | Total Calcium Carbonate equivalent |
| `HWSD2_LAYERS` | `GYPSUM` | REAL | % wt | Yes | -9.0 | None | Gypsum content share |
| `HWSD2_LAYERS` | `ELEC_COND` | REAL | dS/m | Yes | -9.0 | None | Electrical Conductivity |
| `HWSD2_SMU` | `KOPPEN` | TEXT | Code | Yes | None | `D_KOPPEN` | Koppen-Geiger climate classification |
| `HWSD2_SMU` | `WRB2_CODE` | INTEGER | Code | Yes | None | `D_WRB2code` | Dominant Soil Group code |

---

## 2. Conceptual Flattening: One Logical Dataset

To establish a comprehensive scientific representation, we conceptually bypass database normalization and flatten the database relationships into **One Unified Soil Observation**. 

### Resolution of Normalization Boundaries
1. **Spatial to Tabular Translation**: Raster grid resolution decodes geographical latitude and longitude directly to a single `HWSD2_SMU_ID` key.
2. **SMU to Profile Composition**: The `HWSD2_SMU_ID` maps to multiple vertical profile sequences. Each sequence possesses a `SHARE` (%) attribute. The logical observation expands to hold an array of profiles.
3. **Sequence Classification Resolution**: Numeric taxonomy identifiers and phases are resolved against dictionaries (`D_WRB4`, `D_WRB2`, `D_FAO90`, `D_WRB_PHASES`) to embed human-readable scientific labels.
4. **Layer Composition Resolution**: For each profile sequence, the layer rows (`D1` through `D7`) are combined into a vertical array ordered by depth intervals (`TOPDEP` to `BOTDEP`).
5. **Lookup Dictionary Expansion**: Property codes for drainage, root obstacles, impermeable layer bounds, climate zones, and texture classes are mapped to descriptive textual labels.

### One Logical Soil Observation Schema
This conceptual record structures a single coordinate response as follows:
*   **Location Coordinates**: Latitude, Longitude
*   **Climate Zone**: Koppen-Geiger Climate Zone (code + name)
*   **Profiles**: List of:
    *   **Composition Share**: Percentage share of profile in SMU area
    *   **Sequence Index**: Order of profile (1 to N)
    *   **Taxonomy & Classification**:
        *   WRB 2022 (4-digit, 2-digit, phases, group names)
        *   FAO 1990 classification
        *   National Soil Classification symbols
    *   **Agricultural & Hydraulic Limits**:
        *   Drainage rating (class + description)
        *   Impermeable layer depth class
        *   Obstacles to root depth
        *   Water regime class
        *   Soil phase modifier 1 & 2
    *   **Layers**: Stack of vertical depth layers (top to bottom depth in cm), containing:
        *   **USDA/SOTER Texture Classes** (names + codes)
        *   **Physical Properties**: Coarse fragments, Sand, Silt, Clay, Bulk density, Reference bulk density.
        *   **Chemical Properties**: pH (water), Organic carbon, Total nitrogen, C/N ratio, CEC soil, CEC clay, Effective CEC, TEB, Base saturation, Aluminum saturation, ESP, Calcium carbonate, Gypsum, Electrical conductivity.

---

## 3. Scientific Information Hierarchy

The master information model organizes scientific attributes in a hierarchical structure representing scientific meaning rather than database structure:

```
Observation
└── Environmental Context
└── Profiles
    ├── Soil Classification
    ├── Hydrologic Context
    ├── Land Limitations
    └── Soil Layers
        ├── Soil Texture
        ├── Physical Properties
        ├── Chemical Properties
        └── Hydraulic Properties
```
