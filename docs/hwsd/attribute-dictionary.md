# Attribute Dictionary: HWSD v2.0

---

## Document Metadata
*   **Purpose**: Establish a domain-oriented dictionary mapping database fields to scientific meanings, units, and ranges.
*   **Audience**: GIS database engineers, scientific modelers, and backend developers.
*   **Assumptions**:
    *   Descriptions and types are aligned with the physical schemas of `HWSD2_LAYERS` and `HWSD2_SMU`.
    *   Scientific meanings are based on standard FAO, USDA, and ISRIC soil terminology.

---

## 1. Identification Attributes

### Database Field: `HWSD2_SMU_ID`
*   **Human-Readable Name**: Soil Mapping Unit ID (v2.0)
*   **Table**: `HWSD2_LAYERS`, `HWSD2_SMU`
*   **Data Type**: INTEGER
*   **Unit**: None
*   **Valid Range**: `2` to `49830`
*   **Example Values**: `1666`, `12707`
*   **Depth Dependent?**: No
*   **Description**: Unique spatial key linking grid cells in the `HWSD2.bil` raster to their corresponding database attributes.
*   **Scientific Meaning**: Serves as the primary spatial reference key. A single Mapping Unit represents a distinct polygon or grid area characterized by a specific combination of soil types and landforms.
*   **Source**: Verified

### Database Field: `WISE30s_SMU_ID`
*   **Human-Readable Name**: Soil Mapping Unit ID (WISE30s)
*   **Table**: `HWSD2_LAYERS`, `HWSD2_SMU`
*   **Data Type**: VARCHAR
*   **Unit**: None
*   **Valid Range**: N/A
*   **Example Values**: `"WD10001666"`, `"WD10012707"`
*   **Depth Dependent?**: No
*   **Description**: Mapping Unit identifier corresponding to the ISRIC WISE 30-arcsecond soil database.
*   **Scientific Meaning**: Provides cross-reference capabilities to legacy ISRIC datasets for historical comparison.
*   **Source**: Verified

### Database Field: `HWSD1_SMU_ID`
*   **Human-Readable Name**: Soil Mapping Unit ID (v1.2)
*   **Table**: `HWSD2_LAYERS`, `HWSD2_SMU`
*   **Data Type**: INTEGER
*   **Unit**: None
*   **Valid Range**: `1` to `16000`
*   **Example Values**: `1666`, `12707`
*   **Depth Dependent?**: No
*   **Description**: Mapping Unit identifier linking records back to the original HWSD version 1.2 database.
*   **Scientific Meaning**: Enables legacy database joins and backward compatibility.
*   **Source**: Verified

---

## 2. Soil Classification Attributes

### Database Field: `WRB4`
*   **Human-Readable Name**: World Reference Base 4-Digit Classification
*   **Table**: `HWSD2_LAYERS`, `HWSD2_SMU`
*   **Data Type**: VARCHAR
*   **Unit**: Class
*   **Valid Range**: Standard WRB codes
*   **Example Values**: `"RGeu"`, `"ALfr"`
*   **Depth Dependent?**: No
*   **Description**: Soil classification symbol under the World Reference Base for Soil Resources (WRB 2022 edition).
*   **Scientific Meaning**: An international standard soil classification system. Codes indicate the reference soil group and key prefix/suffix qualifiers describing specific physical or chemical horizons.
*   **Source**: Verified

### Database Field: `WRB2`
*   **Human-Readable Name**: World Reference Base Dominant Soil Group (2-Digit)
*   **Table**: `HWSD2_LAYERS`, `HWSD2_SMU`
*   **Data Type**: VARCHAR
*   **Unit**: Class
*   **Valid Range**: Standard 2-digit WRB codes
*   **Example Values**: `"RG"` (Regosol), `"AL"` (Alisol)
*   **Depth Dependent?**: No
*   **Description**: High-level grouping code representing the dominant soil class.
*   **Scientific Meaning**: Identifies the primary soil group, representing broad developmental categories (e.g., Regosols are weakly developed soils).
*   **Source**: Verified

### Database Field: `FAO90`
*   **Human-Readable Name**: FAO 1990 Soil Classification Code
*   **Table**: `HWSD2_LAYERS`, `HWSD2_SMU`
*   **Data Type**: VARCHAR
*   **Unit**: Class
*   **Valid Range**: Standard FAO-90 symbols
*   **Example Values**: `"RGe"`, `"ALf"`
*   **Depth Dependent?**: No
*   **Description**: Legacy soil group classification code matching the FAO-UNESCO 1990 Revised Legend.
*   **Scientific Meaning**: Provides legacy reference matching the older international soil classification legend.
*   **Source**: Verified

---

## 3. Physical Properties

### Database Field: `BULK` / `BULK_DENSITY`
*   **Human-Readable Name**: Bulk Density
*   **Table**: `HWSD2_LAYERS` (as `BULK`), `HWSD2_SMU` (as `BULK_DENSITY`)
*   **Data Type**: REAL
*   **Unit**: $\text{g/cm}^3$
*   **Valid Range**: `0.8` to `2.0`
*   **Example Values**: `1.45`, `1.35`
*   **Depth Dependent?**: Yes (`HWSD2_LAYERS` varies across vertical layers)
*   **Description**: The mass of dry soil divided by its total volume (including pores).
*   **Scientific Meaning**: Key indicator of soil compaction and structural density. High values ($>1.6\text{ g/cm}^3$) indicate compaction that can restrict root penetration and water flow.
*   **Source**: Verified

### Database Field: `COARSE`
*   **Human-Readable Name**: Coarse Fragments
*   **Table**: `HWSD2_LAYERS`
*   **Data Type**: INTEGER
*   **Unit**: % volume
*   **Valid Range**: `0` to `100`
*   **Example Values**: `18`, `0`
*   **Depth Dependent?**: Yes
*   **Description**: Percentage volume of mineral fragments larger than 2 mm.
*   **Scientific Meaning**: Influences tillage ease, water holding capacity, and effective root volume. High coarse fragment volumes dilute nutrient storage and accelerate water drainage.
*   **Source**: Verified

### Database Field: `ROOTS`
*   **Human-Readable Name**: Obstacle to Roots
*   **Table**: `HWSD2_LAYERS`, `HWSD2_SMU`
*   **Data Type**: INTEGER
*   **Unit**: cm
*   **Valid Range**: `0` to `200`
*   **Example Values**: `NULL`, `50`
*   **Depth Dependent?**: Yes (in layers)
*   **Description**: The depth at which root growth is physically restricted or blocked.
*   **Scientific Meaning**: Represents the effective biological depth of the soil. Obstacles can be hard rock, petrocalcic horizons, or consolidated claypans.
*   **Source**: Verified

---

## 4. Chemical Properties

### Database Field: `PH_WATER`
*   **Human-Readable Name**: Soil pH (in Water)
*   **Table**: `HWSD2_LAYERS`
*   **Data Type**: REAL
*   **Unit**: $-\log(\text{H}^+)$
*   **Valid Range**: `3.0` to `10.0`
*   **Example Values**: `6.4`, `7.2`
*   **Depth Dependent?**: Yes
*   **Description**: Measure of active soil acidity or alkalinity determined in a soil-water suspension.
*   **Scientific Meaning**: Crucial factor regulating nutrient solubility and biological activity. Neutral pH (`6.0` to `7.5`) is optimal for most crops; extreme values indicate nutrient deficiencies or toxicities.
*   **Source**: Verified

### Database Field: `CEC_SOIL`
*   **Human-Readable Name**: Cation Exchange Capacity (Soil)
*   **Table**: `HWSD2_LAYERS`
*   **Data Type**: INTEGER
*   **Unit**: $\text{cmolc/kg}$
*   **Valid Range**: `1` to `100`
*   **Example Values**: `8`, `25`
*   **Depth Dependent?**: Yes
*   **Description**: Total capacity of the soil to hold exchangeable cations (nutrients like Calcium, Magnesium, Potassium).
*   **Scientific Meaning**: Measures the nutrient holding capacity and buffering potential of the soil against acidification or leaching.
*   **Source**: Verified

### Database Field: `BSAT`
*   **Human-Readable Name**: Base Saturation
*   **Table**: `HWSD2_LAYERS`
*   **Data Type**: INTEGER
*   **Unit**: % of soil CEC
*   **Valid Range**: `0` to `100`
*   **Example Values**: `71`, `95`
*   **Depth Dependent?**: Yes
*   **Description**: The percentage of the soil exchange complex occupied by basic cations ($\text{Ca}^{2+}$, $\text{Mg}^{2+}$, $\text{K}^+$, $\text{Na}^+$).
*   **Scientific Meaning**: Excellent proxy for natural soil fertility. High base saturation ($>50\%$) indicates alkaline or neutral soils rich in plant nutrients.
*   **Source**: Verified

---

## 5. Water Properties

### Database Field: `AWC`
*   **Human-Readable Name**: Available Water Capacity
*   **Table**: `HWSD2_LAYERS` (as `AWC `), `HWSD2_SMU` (as `AWC`)
*   **Data Type**: INTEGER
*   **Unit**: $\text{mm}$ (in layers) or $\text{mm/m}$ (in SMU)
*   **Valid Range**: `10` to `300`
*   **Example Values**: `168`, `152`
*   **Depth Dependent?**: Yes
*   **Description**: The volume of water that a soil can store and subsequently release to plant roots.
*   **Scientific Meaning**: Evaluates drought resilience. Represents the difference between soil moisture at field capacity and permanent wilting point.
*   **Source**: Verified

### Database Field: `DRAINAGE`
*   **Human-Readable Name**: Reference Soil Drainage Class
*   **Table**: `HWSD2_LAYERS`, `HWSD2_SMU`
*   **Data Type**: VARCHAR
*   **Unit**: Class
*   **Valid Range**: Lookup code in `D_DRAINAGE`
*   **Example Values**: `"MW"` (Moderately Well Drained), `"W"` (Well Drained)
*   **Depth Dependent?**: No
*   **Description**: The rate and extent at which water is removed from the soil under natural conditions.
*   **Scientific Meaning**: Determines water logging risk and aeration. Vital for agricultural zoning and construction suitability.
*   **Source**: Verified

---

## 6. Organic Matter Attributes

### Database Field: `ORG_CARBON`
*   **Human-Readable Name**: Organic Carbon Content
*   **Table**: `HWSD2_LAYERS`
*   **Data Type**: REAL
*   **Unit**: % weight
*   **Valid Range**: `0.01` to `50.0`
*   **Example Values**: `0.431`, `1.25`
*   **Depth Dependent?**: Yes
*   **Description**: Percentage weight of organic carbon present in the soil.
*   **Scientific Meaning**: Direct indicator of soil organic matter (SOM) concentration. Essential for evaluating soil structural stability, biological health, and carbon sink capabilities.
*   **Source**: Verified

---

## 7. Texture Attributes

### Database Field: `SAND` / `SILT` / `CLAY`
*   **Human-Readable Name**: Sand / Silt / Clay Percentages
*   **Table**: `HWSD2_LAYERS`
*   **Data Type**: INTEGER
*   **Unit**: % weight
*   **Valid Range**: `0` to `100` (must sum to 100 per row)
*   **Example Values**: `SAND: 68`, `SILT: 18`, `CLAY: 14`
*   **Depth Dependent?**: Yes
*   **Description**: Particle size distribution representing the weight fractions of Sand ($0.05$–$2.0\text{ mm}$), Silt ($0.002$–$0.05\text{ mm}$), and Clay ($<0.002\text{ mm}$).
*   **Scientific Meaning**: Fundamental physical property. Determines soil water retention, drainage rates, fertility potential, aeration, and engineering stability.
*   **Source**: Verified

### Database Field: `TEXTURE_USDA`
*   **Human-Readable Name**: USDA Texture Class Code
*   **Table**: `HWSD2_LAYERS`, `HWSD2_SMU`
*   **Data Type**: INTEGER
*   **Unit**: Class
*   **Valid Range**: `1` to `12` (lookup code in `D_TEXTURE_USDA`)
*   **Example Values**: `11`, `7`
*   **Depth Dependent?**: Yes (in layers; in `HWSD2_SMU` it represents Topsoil Texture)
*   **Description**: Categorical code representing the soil texture class defined by the United States Department of Agriculture.
*   **Scientific Meaning**: Grouping based on the relative proportions of sand, silt, and clay (e.g., Loam, Clay Loam, Sandy Clay).
*   **Source**: Verified

---

## 8. Layer Metadata

### Database Field: `LAYER`
*   **Human-Readable Name**: Depth Layer Interval
*   **Table**: `HWSD2_LAYERS`
*   **Data Type**: VARCHAR
*   **Unit**: None
*   **Valid Range**: `"D1"` to `"D7"`
*   **Example Values**: `"D2"`
*   **Depth Dependent?**: Yes (acts as the layer grouping key)
*   **Description**: Categorical vertical interval segment identifier.
*   **Scientific Meaning**: Identifies the specific depth range of the measurements (D1: 0–20, D2: 20–40, D3: 40–60, D4: 60–80, D5: 80–100, D6: 100–150, D7: 150–200 cm).
*   **Source**: Verified

### Database Field: `TOPDEP` / `BOTDEP`
*   **Human-Readable Name**: Top Depth / Bottom Depth
*   **Table**: `HWSD2_LAYERS`
*   **Data Type**: INTEGER
*   **Unit**: cm
*   **Valid Range**: `0` to `200`
*   **Example Values**: `TOPDEP: 20`, `BOTDEP: 40`
*   **Depth Dependent?**: Yes
*   **Description**: The upper and lower vertical boundary depths of the respective layer.
*   **Scientific Meaning**: Confirms the vertical dimensions of the soil profile slice.
*   **Source**: Verified

---

## 9. Quality & Coverage Flags

### Database Field: `COVERAGE`
*   **Human-Readable Name**: Geographic Coverage Code
*   **Table**: `HWSD2_LAYERS`, `HWSD2_SMU`
*   **Data Type**: INTEGER
*   **Unit**: Class
*   **Valid Range**: Lookup key in `D_COVERAGE`
*   **Example Values**: `4`, `3`
*   **Depth Dependent?**: No
*   **Description**: Code indicating the source database registry quality, reliability, and mapping detail level.
*   **Scientific Meaning**: Represents the data lineage and scale reliability of the regional survey input.
*   **Source**: Inferred

### Database Field: `PHASE1` / `PHASE2`
*   **Human-Readable Name**: Soil Phase Constraint 1 / 2
*   **Table**: `HWSD2_LAYERS`, `HWSD2_SMU`
*   **Data Type**: INTEGER
*   **Unit**: Class
*   **Valid Range**: Lookup keys in `D_PHASE`
*   **Example Values**: `NULL`, `12`
*   **Depth Dependent?**: No
*   **Description**: Code indicating specific local physical constraints (e.g., gravelly, stony, sodic, saline).
*   **Scientific Meaning**: Flags localized constraints that modify crop suitability and land management operations.
*   **Source**: Verified

---

## 10. Unknown Attributes

The following columns in the primary tables have sparse data or lack clear descriptions in the technical metadata, requiring further investigation:

1.  **`HWSD2_LAYERS.NSC`**:
    *   *Observation*: Appears in actual database column headers but is completely omitted from the metadata dictionary table (`HWSD2_LAYERS_METADATA`).
    *   *Uncertainty*: The exact domain reference and whether it differs functionally from `NSC_MU_SOURCE1/2` is unclear.
2.  **`HWSD2_SMU.WRB2_CODE`**:
    *   *Observation*: Referenced as Dominant Soil Group (WRB + PHASES), pointing to lookup table `D_WRB2code`.
    *   *Uncertainty*: We need to verify if this code differs from standard `WRB2` or contains redundant classification combinations.
3.  **`WRB_Layer` & `WRB_Library` (All Columns)**:
    *   *Observation*: These tables contain only a single row of metadata.
    *   *Uncertainty*: It is unclear if they are leftovers from the GIS creation project or provide essential configuration pathways for mapping layers.
