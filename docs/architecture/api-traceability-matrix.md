# Public API Traceability Matrix

This document provides a complete traceability matrix for all public fields in the Global Soil Explorer API contract. It serves as the permanent API reference, defining the scientific attributes, structural ownership, domain objects, underlying SQLite sources, lookup mappings, units, nullability, and planned frontend components.

---

## Traceability Matrix Table

| API JSON Field | Scientific Attribute | Owner | Domain Object | SQLite Source | Lookup Table | Unit | Nullable | Frontend Component |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :--- |
| **`coordinate.latitude`** | Geographic latitude coordinate | GIS / Geolocation | `Coordinate` | Raster Lookup center | None | Decimal Degrees | No | Map Explorer / Location search |
| **`coordinate.longitude`** | Geographic longitude coordinate | GIS / Geolocation | `Coordinate` | Raster Lookup center | None | Decimal Degrees | No | Map Explorer / Location search |
| **`environmental_context.koppen_climate`** | Koppen-Geiger climate classification | Climatology | `EnvironmentalContext` | `HWSD2_SMU.KOPPEN` | `D_KOPPEN` | None | Yes | Climate profile badge |
| **`metadata.coverage_description`** | Geographic map source coverage description | Provenance | `DatasetMetadata` | `HWSD2_SMU.COVERAGE` | `D_COVERAGE` | None | Yes | Metadata attribution card |
| **`metadata.library`** | Soil taxonomy library reference standard | Provenance | `DatasetMetadata` | `HWSD2_SMU.WRB2_CODE` | `WRB_Library` | None | Yes | Metadata attribution card |
| **`metadata.source`** | active soil database name | Provenance | `DatasetMetadata` | Constant | None | None | Yes | Metadata attribution card |
| **`metadata.dataset_version`** | active soil database version | Provenance | `DatasetMetadata` | Constant | None | None | Yes | Metadata attribution card |
| **`metadata.reference_identifiers`** | Scientific polygon mapping identifier | Provenance | `DatasetMetadata` | `HWSD2_LAYERS.HWSD2_SMU_ID` | None | None | Yes | Metadata attribution card |
| **`profiles[].composition_share`** | Profile share of the mapping unit area | Soil Survey | `SoilProfile` | `HWSD2_LAYERS.SHARE` | None | % | Yes | Profile selector tabs |
| **`profiles[].sequence_index`** | Profile sequence dominance rank | Soil Survey | `SoilProfile` | `HWSD2_LAYERS.SEQUENCE` | None | None | Yes | Profile selector tabs |
| **`profiles[].classification.taxonomy_standard`** | Soil classification standard name | Taxonomy | `SoilClassification` | Derived | None | None | No | Profile classification card |
| **`profiles[].classification.class_name`** | Resolved standard soil taxonomy class | Taxonomy | `SoilClassification` | `WRB4` or `WRB2` or `FAO90` | `D_WRB4` / `D_WRB2` / `D_FAO90` | None | No | Profile classification card |
| **`profiles[].classification.wrb4_name`** | Resolved WRB 2022 taxonomy class | Taxonomy | `SoilClassification` | `HWSD2_LAYERS.WRB4` | `D_WRB4` | None | Yes | Soil taxonomy table |
| **`profiles[].classification.wrb2_name`** | Resolved WRB 2006 taxonomy class | Taxonomy | `SoilClassification` | `HWSD2_LAYERS.WRB2` | `D_WRB2` | None | Yes | Soil taxonomy table |
| **`profiles[].classification.fao90_name`** | Resolved FAO 1990 taxonomy class | Taxonomy | `SoilClassification` | `HWSD2_LAYERS.FAO90` | `D_FAO90` | None | Yes | Soil taxonomy table |
| **`profiles[].classification.wrb_phase_name`** | Resolved WRB soil phase description | Taxonomy | `SoilClassification` | `HWSD2_LAYERS.WRB_PHASES` | `D_WRB_PHASES` | None | Yes | Soil taxonomy table |
| **`profiles[].classification.national_classification`** | National soil taxonomy classification | Taxonomy | `SoilClassification` | `HWSD2_LAYERS.NSC` | None | None | Yes | Soil taxonomy table |
| **`profiles[].hydrologic_context.drainage_description`** | Natural soil drainage class description | Hydrology | `HydrologicContext` | `HWSD2_LAYERS.DRAINAGE` | `D_DRAINAGE` | None | Yes | Profile hydrology widget |
| **`profiles[].hydrologic_context.water_regime_description`** | Water regime description | Hydrology | `HydrologicContext` | `HWSD2_LAYERS.SWR` | `D_SWR` | None | Yes | Profile hydrology widget |
| **`profiles[].hydrologic_context.impermeable_layer_description`** | Impermeable layer depth constraints | Hydrology | `HydrologicContext` | `HWSD2_LAYERS.IL` | `D_IL` | None | Yes | Profile hydrology widget |
| **`profiles[].land_limitations.root_depth_description`** | Accessible plant root depth | Agronomy | `LandLimitations` | `HWSD2_LAYERS.ROOT_DEPTH` | `D_ROOT_DEPTH` | None | Yes | Agronomic limitations panel |
| **`profiles[].land_limitations.root_obstacles_description`** | Mechanical root obstacles | Agronomy | `LandLimitations` | `HWSD2_LAYERS.ROOTS` | `D_ROOTS` | None | Yes | Agronomic limitations panel |
| **`profiles[].land_limitations.phase1_description`** | Agronomic soil modifier phase 1 | Agronomy | `LandLimitations` | `HWSD2_LAYERS.PHASE1` | `D_PHASE` | None | Yes | Agronomic limitations panel |
| **`profiles[].land_limitations.phase2_description`** | Agronomic soil modifier phase 2 | Agronomy | `LandLimitations` | `HWSD2_LAYERS.PHASE2` | `D_PHASE` | None | Yes | Agronomic limitations panel |
| **`profiles[].land_limitations.additional_property_description`** | Additional agronomic property modifier | Agronomy | `LandLimitations` | `HWSD2_LAYERS.ADD_PROP` | `D_ADD_PROP` | None | Yes | Agronomic limitations panel |
| **`profiles[].layers[].top_depth_cm`** | Vertical layer top depth boundary | Physical | `SoilLayer` | `HWSD2_LAYERS.TOPDEP` | None | cm | No | Vertical horizon chart Y-Axis |
| **`profiles[].layers[].bottom_depth_cm`** | Vertical layer bottom depth boundary | Physical | `SoilLayer` | `HWSD2_LAYERS.BOTDEP` | None | cm | No | Vertical horizon chart Y-Axis |
| **`profiles[].layers[].texture.usda_texture_description`** | Resolved USDA texture class description | Physical | `SoilTexture` | `HWSD2_LAYERS.TEXTURE_USDA` | `D_TEXTURE_USDA` | None | Yes | Soil texture diagram |
| **`profiles[].layers[].texture.soter_texture_description`** | Resolved SOTER texture class description | Physical | `SoilTexture` | `HWSD2_LAYERS.TEXTURE_SOTER` | `D_TEXTURE_SOTER` | None | Yes | Soil texture diagram |
| **`profiles[].layers[].measurements.physical.sand`** | Weight share of sand fraction | Physical | `PhysicalProperties` | `HWSD2_LAYERS.SAND` | None | % | Yes | Particle size chart / Layer table |
| **`profiles[].layers[].measurements.physical.silt`** | Weight share of silt fraction | Physical | `PhysicalProperties` | `HWSD2_LAYERS.SILT` | None | % | Yes | Particle size chart / Layer table |
| **`profiles[].layers[].measurements.physical.clay`** | Weight share of clay fraction | Physical | `PhysicalProperties` | `HWSD2_LAYERS.CLAY` | None | % | Yes | Particle size chart / Layer table |
| **`profiles[].layers[].measurements.physical.coarse_fragments`** | Volume share of coarse fragments | Physical | `PhysicalProperties` | `HWSD2_LAYERS.COARSE` | None | % | Yes | Layer physical properties table |
| **`profiles[].layers[].measurements.physical.bulk_density`** | Bulk density of the soil | Physical | `PhysicalProperties` | `HWSD2_LAYERS.BULK` | None | g/cm³ | Yes | Layer physical properties table |
| **`profiles[].layers[].measurements.physical.ref_bulk_density`** | Reference bulk density | Physical | `PhysicalProperties` | `HWSD2_LAYERS.REF_BULK` | None | g/cm³ | Yes | Layer physical properties table |
| **`profiles[].layers[].measurements.chemical.ph`** | Soil pH value (in water) | Chemical | `ChemicalProperties` | `HWSD2_LAYERS.PH_WATER` | None | pH | Yes | Chemistry stats / pH line chart |
| **`profiles[].layers[].measurements.chemical.organic_carbon`** | Organic carbon share | Chemical | `ChemicalProperties` | `HWSD2_LAYERS.ORG_CARBON` | None | % | Yes | Carbon stats / SOC line chart |
| **`profiles[].layers[].measurements.chemical.total_nitrogen`** | Total nitrogen concentration | Chemical | `ChemicalProperties` | `HWSD2_LAYERS.TOTAL_N` | None | g/kg | Yes | Chemistry stats table |
| **`profiles[].layers[].measurements.chemical.cn_ratio`** | Carbon-to-nitrogen ratio | Chemical | `ChemicalProperties` | `HWSD2_LAYERS.CN_RATIO` | None | None | Yes | Chemistry stats table |
| **`profiles[].layers[].measurements.chemical.cec_soil`** | Cation exchange capacity of soil | Chemical | `ChemicalProperties` | `HWSD2_LAYERS.CEC_SOIL` | None | cmol(+)/kg | Yes | Chemistry stats table |
| **`profiles[].layers[].measurements.chemical.cec_clay`** | Cation exchange capacity of clay fraction | Chemical | `ChemicalProperties` | `HWSD2_LAYERS.CEC_CLAY` | None | cmol(+)/kg | Yes | Chemistry stats table |
| **`profiles[].layers[].measurements.chemical.effective_cec`** | Effective Cation Exchange Capacity | Chemical | `ChemicalProperties` | `HWSD2_LAYERS.CEC_EFF` | None | cmol(+)/kg | Yes | Chemistry stats table |
| **`profiles[].layers[].measurements.chemical.teb`** | Total exchangeable bases | Chemical | `ChemicalProperties` | `HWSD2_LAYERS.TEB` | None | cmol(+)/kg | Yes | Chemistry stats table |
| **`profiles[].layers[].measurements.chemical.base_saturation`** | Base saturation index | Chemical | `ChemicalProperties` | `HWSD2_LAYERS.BSAT` | None | % | Yes | Chemistry stats table |
| **`profiles[].layers[].measurements.chemical.aluminum_saturation`** | Aluminum saturation index | Chemical | `ChemicalProperties` | `HWSD2_LAYERS.ALUM_SAT` | None | % | Yes | Chemistry stats table |
| **`profiles[].layers[].measurements.chemical.esp`** | Exchangeable sodium percentage | Chemical | `ChemicalProperties` | `HWSD2_LAYERS.ESP` | None | % | Yes | Chemistry stats table |
| **`profiles[].layers[].measurements.chemical.calcium_carbonate`** | Calcium carbonate equivalent | Chemical | `ChemicalProperties` | `HWSD2_LAYERS.TCARBON_EQ`| None | % | Yes | Chemistry stats table |
| **`profiles[].layers[].measurements.chemical.gypsum`** | Gypsum weight share | Chemical | `ChemicalProperties` | `HWSD2_LAYERS.GYPSUM` | None | % | Yes | Chemistry stats table |
| **`profiles[].layers[].measurements.chemical.electrical_conductivity`** | Electrical conductivity | Chemical | `ChemicalProperties` | `HWSD2_LAYERS.ELEC_COND` | None | dS/m | Yes | Chemistry stats table |
| **`profiles[].layers[].measurements.hydraulic.available_water_capacity`** | Available water capacity | Hydraulic | `HydraulicProperties` | `HWSD2_LAYERS.AWC` | None | mm | Yes | Water holding capacity chart |

---

## Grouped Codes Block reference (nested `codes` schemas)

For every schema model where raw codes are retained alongside standard descriptive scientific names, they are grouped in a nested `codes` block. This keeps the primary level of the JSON payload completely clean, standard, and descriptive.

### 1. `metadata.codes` (`DatasetMetadataCodes`)
*   `coverage`: Raw national dataset coverage source integer code.

### 2. `profiles[].classification.codes` (`SoilClassificationCodes`)
*   `class_symbol`: Primary taxonomic classification symbol code.
*   `wrb4_code`: WRB 2022 classification code.
*   `wrb2_code`: WRB 2006 classification code.
*   `fao90_code`: FAO 1990 classification code.
*   `wrb_phase_code`: WRB soil phase classification code.
*   `dominant_group_code`: Dominated soil group code prefix.

### 3. `profiles[].hydrologic_context.codes` (`HydrologicContextCodes`)
*   `drainage`: Raw drainage class symbol code (e.g. "MW", "W").
*   `water_regime`: Raw water regime class integer code.
*   `impermeable_layer`: Raw impermeable layer depth constraint class code.

### 4. `profiles[].land_limitations.codes` (`LandLimitationsCodes`)
*   `root_depth`: Raw root depth class integer code.
*   `root_obstacles`: Raw mechanical root obstacles class code.
*   `phase1`: Raw soil phase modifier limitation class code 1.
*   `phase2`: Raw soil phase modifier limitation class code 2.
*   `additional_property`: Raw additional property constraint modifier code.

### 5. `profiles[].layers[].texture.codes` (`SoilTextureCodes`)
*   `usda_texture`: Raw USDA texture class integer code.
*   `soter_texture`: Raw SOTER texture class letter code (e.g. "M", "F").
