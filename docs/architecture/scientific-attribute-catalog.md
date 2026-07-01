# Scientific Attribute Catalog

This catalog lists every unique scientific attribute derived from the official HWSD v2.0 dataset, classifying it by its operational behavior (Static, Depth-dependent, Derived, Lookup/Reference, Visualization) and detailing its current integration status in the API.

---

## 1. Summary Statistics

*   **Total Tables in SQLite**: 25
*   **Total Core Physical Columns**: 71
*   **Duplicate Columns Removed**: 21 (aggregated fields in `HWSD2_SMU` that mirror `HWSD2_LAYERS`)
*   **Lookup Expansions**: 18 lookup dictionary mappings
*   **Final Unique Scientific Attributes**: 46
*   **Number of Scientific Groups**: 11

---

## 2. Master Attribute Catalog

### Group 1: General & Location
| Attribute Name | Variable Key | Attribute Type | Current API Status | Scientific Purpose |
| :--- | :--- | :--- | :--- | :--- |
| Latitude | `latitude` | Static | `✓ Exposed` | Coordinate reference (y-axis) |
| Longitude | `longitude` | Static | `✓ Exposed` | Coordinate reference (x-axis) |
| Climate Zone | `KOPPEN` | Static | `✗ Missing` | Koppen-Geiger climate classification |

### Group 2: Taxonomic Classification
| Attribute Name | Variable Key | Attribute Type | Current API Status | Scientific Purpose |
| :--- | :--- | :--- | :--- | :--- |
| Taxonomy Standard | `taxonomy` | Static | `✓ Exposed` | Identifies classification standard used |
| Soil Group Code | `WRB4` / `WRB2` / `FAO90` | Static | `✓ Exposed` | Taxonomic group symbol |
| Soil Group Name | lookup label | Lookup/Reference | `✓ Exposed` | Translated taxonomic group label |
| Soil Phase Modifier | `WRB_PHASES` | Static | `✗ Missing` | Detailed WRB phase descriptor symbol |
| Dominant Group Code | `WRB2_CODE` | Static | `✗ Missing` | Dominant WRB group reference code |
| National Classification| `NSC` | Static | `✗ Missing` | Native national classification code |

### Group 3: Profile Composition
| Attribute Name | Variable Key | Attribute Type | Current API Status | Scientific Purpose |
| :--- | :--- | :--- | :--- | :--- |
| Composition Share | `SHARE` | Static | `✓ Exposed` | Share (%) of profile in mapping unit area |
| Profile Sequence | `SEQUENCE` | Static | `✓ Exposed` | Index rank (1 to N) of profile in SMU |

### Group 4: Hydrology & Water
| Attribute Name | Variable Key | Attribute Type | Current API Status | Scientific Purpose |
| :--- | :--- | :--- | :--- | :--- |
| Soil Drainage Class | `DRAINAGE` | Static | `✗ Missing` | Natural drainage class descriptor |
| Soil Water Regime | `SWR` | Static | `✗ Missing` | Water saturation characteristics |
| Impermeable Layer | `IL` | Static | `✗ Missing` | Depth class to impermeable boundary |

### Group 5: Agronomic Constraints & Limitations
| Attribute Name | Variable Key | Attribute Type | Current API Status | Scientific Purpose |
| :--- | :--- | :--- | :--- | :--- |
| Rootable Soil Depth | `ROOT_DEPTH` | Static | `✗ Missing` | Total soil depth accessible by plant roots |
| Obstacle to Roots | `ROOTS` | Static | `✗ Missing` | Type of mechanical obstacle to roots |
| Phase modifier 1 | `PHASE1` | Static | `✗ Missing` | Soil phase limitation 1 (e.g., salinity) |
| Phase modifier 2 | `PHASE2` | Static | `✗ Missing` | Soil phase limitation 2 |
| Additional Properties | `ADD_PROP` | Static | `✗ Missing` | Soil restriction qualifiers |

### Group 6: Layer Boundaries
| Attribute Name | Variable Key | Attribute Type | Current API Status | Scientific Purpose |
| :--- | :--- | :--- | :--- | :--- |
| Top Boundary | `TOPDEP` | Depth-dependent | `✓ Exposed` | Start depth of soil layer (cm) |
| Bottom Boundary | `BOTDEP` | Depth-dependent | `✓ Exposed` | End depth of soil layer (cm) |

### Group 7: Soil Texture
| Attribute Name | Variable Key | Attribute Type | Current API Status | Scientific Purpose |
| :--- | :--- | :--- | :--- | :--- |
| USDA Texture Class | `TEXTURE_USDA` | Depth-dependent | `✗ Missing` | Texture group (USDA standard) |
| SOTER Texture Class | `TEXTURE_SOTER`| Depth-dependent | `✗ Missing` | Texture group (SOTER standard) |

### Group 8: Physical Properties (Layer-Specific)
| Attribute Name | Variable Key | Attribute Type | Current API Status | Scientific Purpose |
| :--- | :--- | :--- | :--- | :--- |
| Coarse Fragments | `COARSE` | Depth-dependent | `✓ Exposed` | Volume percent of gravel (>2mm) |
| Sand Content | `SAND` | Depth-dependent | `✓ Exposed` | Weight percent of sand fraction |
| Silt Content | `SILT` | Depth-dependent | `✓ Exposed` | Weight percent of silt fraction |
| Clay Content | `CLAY` | Depth-dependent | `✓ Exposed` | Weight percent of clay fraction |
| Bulk Density | `BULK` | Depth-dependent | `✓ Exposed` | Soil dry mass per unit volume ($g/cm^3$) |
| Reference Bulk Density| `REF_BULK` | Depth-dependent | `✗ Missing` | Baseline uncompacted density ($g/cm^3$) |

### Group 9: Chemical Properties (Layer-Specific)
| Attribute Name | Variable Key | Attribute Type | Current API Status | Scientific Purpose |
| :--- | :--- | :--- | :--- | :--- |
| pH (Water) | `PH_WATER` | Depth-dependent | `✓ Exposed` | Acidity measured in water extraction |
| Organic Carbon | `ORG_CARBON` | Depth-dependent | `✓ Exposed` | Organic carbon weight share (%) |
| Total Nitrogen | `TOTAL_N` | Depth-dependent | `✗ Missing` | Nitrogen concentration ($g/kg$) |
| Carbon-Nitrogen Ratio | `CN_RATIO` | Stored | `✗ Missing` | Ratio of Organic Carbon to Total Nitrogen |
| CEC (Soil) | `CEC_SOIL` | Depth-dependent | `✓ Exposed` | Cation Exchange Capacity ($cmolc/kg$) |
| CEC (Clay) | `CEC_CLAY` | Depth-dependent | `✗ Missing` | CEC of clay fraction ($cmolc/kg$) |
| Effective CEC | `CEC_EFF` | Depth-dependent | `✗ Missing` | Effective Cation Exchange Capacity ($cmolc/kg$) |
| Total Exchangeable Bases| `TEB` | Depth-dependent | `✗ Missing` | Sum of exchangeable bases ($cmolc/kg$) |
| Base Saturation | `BSAT` | Depth-dependent | `✓ Exposed` | Percent of CEC occupied by basic cations |
| Aluminum Saturation | `ALUM_SAT` | Depth-dependent | `✗ Missing` | Aluminum saturation index (%) |
| Sodium Percentage | `ESP` | Depth-dependent | `✗ Missing` | Exchangeable Sodium Percentage (%) |
| Calcium Carbonate | `TCARBON_EQ` | Depth-dependent | `✗ Missing` | Calcium carbonate equivalent (%) |
| Gypsum Content | `GYPSUM` | Depth-dependent | `✗ Missing` | Gypsum fraction weight share (%) |
| Electrical Conductivity| `ELEC_COND` | Depth-dependent | `✗ Missing` | Salinity index ($dS/m$) |

### Group 10: Hydraulic Properties
| Attribute Name | Variable Key | Attribute Type | Current API Status | Scientific Purpose |
| :--- | :--- | :--- | :--- | :--- |
| Available Water Capacity| `AWC` | Depth-dependent | `✓ Exposed` | Water available for root uptake ($mm$) |

### Group 11: Dataset Metadata & Reference
| Attribute Name | Variable Key | Attribute Type | Current API Status | Scientific Purpose |
| :--- | :--- | :--- | :--- | :--- |
| Map Coverage Source | `COVERAGE` | Lookup/Reference | `✗ Missing` | Source region database reference |
| Master Library ID | `WRB_Library` | Lookup/Reference | `✗ Missing` | Dataset metadata identifier |

### Group 12: Visualization Metadata
| Attribute Name | Variable Key | Attribute Type | Current API Status | Scientific Purpose |
| :--- | :--- | :--- | :--- | :--- |
| Soil Group Colors | RGB channels | Visualization metadata | `✗ Missing` | Rendering colors for GIS map |
