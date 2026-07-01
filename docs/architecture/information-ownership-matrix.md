# Information Ownership Matrix

This matrix maps every unique scientific attribute in the HWSD v2.0 dataset to its domain owner, lifecycle status, scientific group, and current/future API and frontend states.

---

## 1. Lifecycle Definition Definitions
*   **Stored**: Physical values read directly from raster seek offsets or database columns.
*   **Lookup**: Scientific names or translations resolved from separate dictionaries using codes.
*   **Computed**: Mathematically derived fields computed at runtime (e.g., C/N ratio, if not stored, or texture classification derived from sand/silt/clay percentages).
*   **Dataset Metadata**: Provenance or source database reference indicators.
*   **Visualization Only**: Color codes, rendering schemas, and display legends.

---

## 2. Master Matrix (46 Attributes)

| Attribute Name | Owner | Lifecycle | Scientific Group | Current Backend | Future API Status | Future Frontend Section |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Latitude | `Coordinate` | Stored | General & Location | `✓ Exposed` | Included | General |
| Longitude | `Coordinate` | Stored | General & Location | `✓ Exposed` | Included | General |
| Climate Zone (Code) | `EnvironmentalContext` | Stored | General & Location | `✗ Missing` | Included | Environment |
| Climate Zone (Name) | `EnvironmentalContext` | Lookup | General & Location | `✗ Missing` | Included | Environment |
| WRB 2022 (4-digit code) | `SoilClassification` | Stored | Taxonomic | `✓ Exposed` | Included | Classification |
| WRB 2022 (4-digit name) | `SoilClassification` | Lookup | Taxonomic | `✓ Exposed` | Included | Classification |
| WRB 2022 (2-digit code) | `SoilClassification` | Stored | Taxonomic | `✓ Exposed` | Included | Classification |
| WRB 2022 (2-digit name) | `SoilClassification` | Lookup | Taxonomic | `✓ Exposed` | Included | Classification |
| FAO 1990 Code | `SoilClassification` | Stored | Taxonomic | `✓ Exposed` | Included | Classification |
| FAO 1990 Name | `SoilClassification` | Lookup | Taxonomic | `✓ Exposed` | Included | Classification |
| WRB Phase Symbols | `SoilClassification` | Stored | Taxonomic | `✗ Missing` | Optional | Classification |
| WRB Phase Names | `SoilClassification` | Lookup | Taxonomic | `✗ Missing` | Optional | Classification |
| Dominant Soil Group Code| `SoilClassification` | Stored | Taxonomic | `✗ Missing` | Included | Classification |
| National Classification | `SoilClassification` | Stored | Taxonomic | `✗ Missing` | Optional | Classification |
| Composition Share (%) | `SoilProfile` | Stored | Profile Composition | `✓ Exposed` | Included | Profiles |
| Profile Sequence Index | `SoilProfile` | Stored | Profile Composition | `✓ Exposed` | Included | Profiles |
| Soil Drainage Class | `HydrologicContext` | Stored | Hydrology & Water | `✗ Missing` | Included | Hydrology |
| Soil Drainage Name | `HydrologicContext` | Lookup | Hydrology & Water | `✗ Missing` | Included | Hydrology |
| Soil Water Regime Class | `HydrologicContext` | Stored | Hydrology & Water | `✗ Missing` | Optional | Hydrology |
| Soil Water Regime Name | `HydrologicContext` | Lookup | Hydrology & Water | `✗ Missing` | Optional | Hydrology |
| Impermeable Layer Class | `HydrologicContext` | Stored | Hydrology & Water | `✗ Missing` | Included | Hydrology |
| Impermeable Layer Name | `HydrologicContext` | Lookup | Hydrology & Water | `✗ Missing` | Included | Hydrology |
| Rootable Soil Depth Class| `LandLimitation` | Stored | Limitations | `✗ Missing` | Included | Limitations |
| Rootable Soil Depth Name | `LandLimitation` | Lookup | Limitations | `✗ Missing` | Included | Limitations |
| Obstacle to Roots Class | `LandLimitation` | Stored | Limitations | `✗ Missing` | Included | Limitations |
| Obstacle to Roots Name | `LandLimitation` | Lookup | Limitations | `✗ Missing` | Included | Limitations |
| Soil Phase 1 Class | `LandLimitation` | Stored | Limitations | `✗ Missing` | Included | Limitations |
| Soil Phase 1 Name | `LandLimitation` | Lookup | Limitations | `✗ Missing` | Included | Limitations |
| Soil Phase 2 Class | `LandLimitation` | Stored | Limitations | `✗ Missing` | Included | Limitations |
| Soil Phase 2 Name | `LandLimitation` | Lookup | Limitations | `✗ Missing` | Included | Limitations |
| Additional Properties Cls| `LandLimitation` | Stored | Limitations | `✗ Missing` | Optional | Limitations |
| Additional Properties Name| `LandLimitation` | Lookup | Limitations | `✗ Missing` | Optional | Limitations |
| Layer Top Boundary (cm) | `SoilLayer` | Stored | Layer Boundaries | `✓ Exposed` | Included | Layers |
| Layer Bottom Boundary(cm)| `SoilLayer` | Stored | Layer Boundaries | `✓ Exposed` | Included | Layers |
| USDA Texture Class Code | `SoilTexture` | Stored | Soil Texture | `✗ Missing` | Included | Texture |
| USDA Texture Class Name | `SoilTexture` | Lookup | Soil Texture | `✗ Missing` | Included | Texture |
| SOTER Texture Class Code | `SoilTexture` | Stored | Soil Texture | `✗ Missing` | Optional | Texture |
| SOTER Texture Class Name | `SoilTexture` | Lookup | Soil Texture | `✗ Missing` | Optional | Texture |
| Coarse Fragments (% vol) | `PhysicalProperties` | Stored | Physical Properties | `✓ Exposed` | Included | Physical |
| Sand Content (% weight) | `PhysicalProperties` | Stored | Physical Properties | `✓ Exposed` | Included | Physical |
| Silt Content (% weight) | `PhysicalProperties` | Stored | Physical Properties | `✓ Exposed` | Included | Physical |
| Clay Content (% weight) | `PhysicalProperties` | Stored | Physical Properties | `✓ Exposed` | Included | Physical |
| Bulk Density ($g/cm^3$) | `PhysicalProperties` | Stored | Physical Properties | `✓ Exposed` | Included | Physical |
| Reference Bulk Density | `PhysicalProperties` | Stored | Physical Properties | `✗ Missing` | Optional | Physical |
| pH (Water) | `ChemicalProperties`| Stored | Chemical Properties | `✓ Exposed` | Included | Chemical |
| Organic Carbon (% wt) | `ChemicalProperties`| Stored | Chemical Properties | `✓ Exposed` | Included | Chemical |
| Total Nitrogen ($g/kg$) | `ChemicalProperties`| Stored | Chemical Properties | `✗ Missing` | Included | Chemical |
| C/N Ratio (Carbon/Nitrogen)| `ChemicalProperties`| Stored | Chemical Properties | `✗ Missing` | Included | Chemical |
| CEC Soil ($cmolc/kg$) | `ChemicalProperties`| Stored | Chemical Properties | `✓ Exposed` | Included | Chemical |
| CEC Clay ($cmolc/kg$) | `ChemicalProperties`| Stored | Chemical Properties | `✗ Missing` | Optional | Chemical |
| Effective CEC ($cmolc/kg$) | `ChemicalProperties`| Stored | Chemical Properties | `✗ Missing` | Optional | Chemical |
| TEB ($cmolc/kg$) | `ChemicalProperties`| Stored | Chemical Properties | `✗ Missing` | Optional | Chemical |
| Base Saturation (%) | `ChemicalProperties`| Stored | Chemical Properties | `✓ Exposed` | Included | Chemical |
| Aluminum Saturation (%) | `ChemicalProperties`| Stored | Chemical Properties | `✗ Missing` | Optional | Chemical |
| Sodium Percentage (ESP) | `ChemicalProperties`| Stored | Chemical Properties | `✗ Missing` | Optional | Chemical |
| Calcium Carbonate (% wt) | `ChemicalProperties`| Stored | Chemical Properties | `✗ Missing` | Included | Chemical |
| Gypsum Content (% wt) | `ChemicalProperties`| Stored | Chemical Properties | `✗ Missing` | Included | Chemical |
| Electrical Conduct (dS/m)| `ChemicalProperties`| Stored | Chemical Properties | `✗ Missing` | Included | Chemical |
| Available Water (AWC) | `HydraulicProperties`| Stored | Hydraulic Properties| `✓ Exposed` | Included | Hydraulic |
| Map Coverage Source | `DatasetMetadata` | Dataset Metadata | Metadata & Reference | `✗ Missing` | Optional | Metadata |
| Library Reference ID | `DatasetMetadata` | Dataset Metadata | Metadata & Reference | `✗ Missing` | Optional | Metadata |
| Thematic RGB Colors | `VisualizationLegend`| Visualization Only| Visualization | `✗ Missing` | Optional | References |
