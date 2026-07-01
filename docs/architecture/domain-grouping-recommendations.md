# Domain Grouping & Information Architecture Recommendations

This document outlines structural recommendations for evolving the Global Soil Explorer domain model and API schemas based on the Master Information Model Audit. It answers the six core questions regarding dataset flattening, scientific grouping, gaps, and emerging domain objects.

---

## 1. Core Audit Questions Resolved

### Q1: If the entire HWSD dataset were represented as ONE logical soil observation, how many unique scientific attributes would it contain?
It would contain exactly **46 unique scientific attributes** (excluding system keys like internal SQLite `ID` values or duplicate column keys).

### Q2: What are those attributes?
The attributes comprise:
*   *Coordinates & Climate*: Latitude, Longitude, Koppen climate class.
*   *Taxonomy*: Standard, group symbols (WRB4, WRB2, FAO90), phase symbols, group names, dominant group code, and national symbols.
*   *Composition*: share, sequence index.
*   *Hydrology*: drainage rating, impermeable layer depth, water regime class.
*   *Limitations*: rooting depth class, root obstacles, phase modifiers (1 & 2), additional properties.
*   *Boundaries*: top boundary, bottom boundary.
*   *Texture*: USDA texture class, SOTER texture class.
*   *Physicals*: coarse fragments, sand, silt, clay, bulk density, reference bulk density.
*   *Chemicals*: pH (water), organic carbon, total nitrogen, C/N ratio, CEC soil, CEC clay, effective CEC, TEB, base saturation, aluminum saturation, ESP, calcium carbonate equivalent, gypsum, electrical conductivity.
*   *Hydraulics*: available water capacity.
*   *Metadata & Visuals*: coverage source, library ID, map group colors.

### Q3: How should they be grouped scientifically rather than by database table?
They are grouped into **12 Scientific Concepts**:
1.  **General & Location**: Spatial coords and dominant climate zone.
2.  **Taxonomic Classification**: Systems of soil classification (WRB, FAO) and national code groups.
3.  **Profile Composition**: Quantitative spatial composition and indexing.
4.  **Hydrology & Water**: Water movement and barrier depths.
5.  **Agronomic Constraints & Limitations**: Physical, chemical, or depth obstructions to plant roots.
6.  **Layer Boundaries**: Vertical coordinate boundaries.
7.  **Soil Texture**: Soil grain size classification indices.
8.  **Physical Properties**: Soil mechanical parameters.
9.  **Chemical Properties**: Acid-base status, carbon pools, nitrogen content, exchange complex parameters, and mineral concentrations.
10. **Hydraulic Properties**: Root water accessibility.
11. **Dataset Metadata & Reference**: Spatial data source and version mappings.
12. **Visualization Metadata**: Legend coloring schemes.

### Q4: Which attributes are currently exposed by the backend?
*   Coordinates (latitude, longitude)
*   Composition shares and sequence index
*   Taxonomy standard, symbol, and names (WRB4, WRB2, FAO90)
*   Vertical layer boundaries (top/bottom depths)
*   Physical properties (sand, silt, clay, coarse fragments, bulk density)
*   Chemical properties (pH, organic carbon, soil CEC, base saturation)
*   Hydraulics (Available Water Capacity)

### Q5: Which attributes are currently missing?
*   Climate classification (`KOPPEN`)
*   Soil drainage class, water regime, impermeable boundary depth (`DRAINAGE`, `SWR`, `IL`)
*   Agronomic limitations (`ROOTS`, `ROOT_DEPTH`, `PHASE1`, `PHASE2`, `ADD_PROP`)
*   Texture classifications (`TEXTURE_USDA`, `TEXTURE_SOTER`)
*   Nutrients, salinity, and advanced exchange parameters (`TOTAL_N`, `CN_RATIO`, `CEC_CLAY`, `CEC_EFF`, `TEB`, `ALUM_SAT`, `ESP`, `TCARBON_EQ`, `GYPSUM`, `ELEC_COND`)
*   Reference bulk density (`REF_BULK`)
*   Dataset source (`COVERAGE`, `WRB_Library`) and thematic colors (`WRB_Class` RGB channels)

### Q6: Which future domain objects naturally emerge from these scientific groups?
To prevent a single giant `SoilLayer` object and maintain strict dataset-agnosticism, the domain should evolve to wrap properties in these cohesive objects:
1.  **`EnvironmentalContext`**: (Replaces ClimaticMetadata) Captures climate classification (`KOPPEN`) and serves as the generic domain container for non-soil environmental parameters such as future elevation, terrain, land cover, and administrative details.
2.  **`HydrologicContext`**: Groups drainage, water regime, and impermeable layer depth. These attributes share the same scientific theme: they govern the hydrology, aeration, and saturation dynamics of the profile.
3.  **`SoilTexture`**: Maintained as an independent classification object (separate from `PhysicalProperties`). While Sand/Silt/Clay are continuous measurements, Soil Texture is a categorical classification that can be derived or translated via USDA/SOTER standards.
4.  **`LandLimitation`**: Captures agricultural constraints (obstacles to roots, depth limitations, and soil phases).
5.  **`PhysicalProperties`**: Groups sand, silt, clay, coarse fragments, and bulk densities.
6.  **`ChemicalProperties`**: Groups pH, carbon pools, total nitrogen, C/N ratio, cation exchange capacities, bases, calcium carbonate, gypsum, and salinity.
7.  **`DatasetMetadata`**: Groups source provenance data (coverage, library IDs) keeping data origin separate from physical measurements.

> [!IMPORTANT]
> **Visualization Separation**: All visualization attributes (like RGB color channels from `WRB_Class`, display names, or mapping legends) are excluded from the scientific domain. They belong strictly in the **Renderer** or **Frontend** layer, ensuring visual theme changes do not impact domain models.

---

## 2. Re-Architecture Domain Blueprint

```
                     ┌───────────────────┐
                     │  SoilObservation  │
                     └─────────┬─────────┘
                               │ 1..*
                     ┌─────────▼─────────┐
                     │    SoilProfile    ├─────────┐
                     └─────────┬─────────┘         │
                               │ 1..*              ▼
                     ┌─────────▼─────────┐ ┌───────────────┐
                     │     SoilLayer     │ │ LandLimit /   │
                     └─────────┬─────────┘ │ Hydrology /   │
                               │           │ Classification│
            ┌──────────────────┼────────────────┐  └───────────────┘
            ▼                  ▼                ▼
┌──────────────────┐ ┌──────────────────┐ ┌───────────┐
│PhysicalProperties│ │ChemicalProperties│ │SoilTexture│
└──────────────────┘ └──────────────────┘ └───────────┘
```

By decoupling physical properties (grain distribution, densities) and chemical properties (carbon index, nutrient loads, exchange capacities) from the core `SoilLayer` structure, we maintain high modularity, allow clean validation rules per property group, and enable the REST API to serialize sections independently.

---

## 3. Frontend Information Architecture

The frontend dashboard should organize the 46 unique scientific attributes into distinct, user-friendly UI tabs/collapsibles:

1.  **General Context**: Latitude, Longitude, Climate Zone, Map Source.
2.  **Taxonomic Classification**: Dominant WRB Class (with RGB color indicators), FAO90 Class, and Phase symbols.
3.  **Composition & Shares**: Share weight representation of each profile.
4.  **Profile Limitations**: Rooting limitations, impermeable layer depth, and drainage class.
5.  **Layer Properties**:
    *   *Depth Boundaries*: Top and Bottom depth.
    *   *USDA Texture*: USDA Texture Class and SOTER Texture Class.
    *   *Physicals*: Sand/Silt/Clay fractions, coarse fragments, bulk density.
    *   *Chemicals*: pH, organic carbon, total nitrogen, C/N ratio, CEC, base saturation, gypsum, salinity.
