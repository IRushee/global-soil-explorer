# Scientific Architecture Freeze Report

This document freezes the scientific architecture and information model for the Global Soil Explorer backend. It contains the final cardinality audit, lookup-metadata separation rules, future dataset compatibility analysis, master statistics, and the final approval checklist.

---

## 1. Cardinality Audit

Each scientific attribute has been assigned a single, strict cardinality:

*   **Observation-Level** (Global to coordinate/pixel lookup point): Latitude, Longitude, Climate Zone.
*   **Per Profile** (Unique to each soil profile component making up the Soil Mapping Unit): Composition share, sequence index, WRB taxonomy groups (4-digit, 2-digit, phases, codes), FAO90 class, national classifications, drainage class, water regime class, impermeable layer depth, rooting depth constraints, obstacle to roots, and soil phases (1 & 2).
*   **Per Layer** (Varies with soil depth): Vertical depth boundaries (top/bottom), texture classifications, available water capacity, physical fractions (sand, silt, clay, coarse fragment volume, bulk density, reference bulk density), and chemical profiles (pH, organic carbon, total nitrogen, C/N ratio, soil/clay CEC, effective CEC, TEB, base saturation, aluminum saturation, ESP, calcium carbonate equivalent, gypsum, and electrical conductivity).
*   **Dataset-Level** (Applies to the dataset metadata globally): Map coverage source, library reference identifier.
*   **Visualization-Level** (Presentation layer metadata): Thematic RGB color channels.

---

## 2. Dictionary vs. Metadata Boundary Rules

We maintain a strict boundary separating lookup dictionaries from dataset metadata:

1.  **Lookup Dictionaries**: Translate raw stored numeric/string codes to scientific taxonomy labels or classes. These translate properties of the soil (e.g. `D_WRB4` mapping `LV` to `"Luvisols"`, or `D_DRAINAGE` mapping drainage codes to drainage ratings). They are owned by the corresponding soil property domain objects.
2.  **Dataset Metadata**: Provenance, versioning, and map source records (such as `D_COVERAGE` mapping coverage codes to the source database mapping agency, or `WRB_Library` database details). They are owned by `DatasetMetadata` and describe the dataset's origin rather than the soil's physical parameters.

---

## 3. Visualization Decoupling

All visualization properties (RGB values from `WRB_Class`, thematic display legends, icons, or color ramps) are excluded from the core scientific domain.
*   **Decoupling Policy**: Visual properties must remain in the **Renderer** or **Frontend** presentation layers. This allows the backend to serve raw scientific measurements, ensuring that cosmetic theme changes, legend scales, or accessibility adjustments do not affect the domain schema.

---

## 4. Future Dataset Compatibility

All domain objects are designed using standard scientific nomenclature, avoiding HWSD-specific naming conventions:
*   `SoilLayer` boundaries accept arbitrary `top_depth_cm` and `bottom_depth_cm` floats, accommodating standard depths of future datasets like SoilGrids or national archives.
*   Properties use standard `PropertyType` and `Unit` definitions rather than mapping directly to SQLite database columns, allowing the service layer to perform conversion/normalization logic.

---

## 5. Master Information Model Statistics

### A. Counts by Cardinality
*   **Observation-Level Fields**: 4
*   **Per-Profile Fields**: 28
*   **Per-Layer Fields**: 27
*   **Dataset-Level Fields**: 2
*   **Visualization-Level Fields**: 1
*   **Total Resolved UI Fields**: 62

### B. Counts by Lifecycle
*   **Stored (Physical Measurements)**: 31
*   **Lookup (Resolved Code Meanings)**: 28
*   **Dataset Metadata**: 2
*   **Visualization Only**: 1
*   **Total Resolved UI Fields**: 62

### C. Counts by Scientific Groups
*   **General & Location**: 4
*   **Taxonomic Classification**: 10
*   **Profile Composition**: 2
*   **Hydrology & Water**: 6
*   **Agronomic Constraints & Limitations**: 10
*   **Layer Boundaries**: 2
*   **Soil Texture**: 4
*   **Physical Properties**: 6
*   **Chemical Properties**: 15
*   **Hydraulic Properties**: 1
*   **Dataset Metadata & Reference**: 2
*   **Visualization**: 1
*   **Total Resolved UI Fields**: 62

---

## 6. Final Approval Checklist

1.  **Is every scientific attribute represented exactly once?**
    **YES**. The master matrix accounts for all elements without double-counting.
2.  **Does every attribute have exactly one owner?**
    **YES**. Every attribute maps to a single domain object container.
3.  **Does every attribute have exactly one lifecycle?**
    **YES**. Lifecycles are clearly defined (Stored, Lookup, Dataset Metadata, Visualization).
4.  **Does every attribute have exactly one cardinality?**
    **YES**. Clear boundaries separate coordinate-level, profile-level, and layer-level scopes.
5.  **Are visualization concerns fully separated?**
    **YES**. Thematic RGB colors are isolated to presentation and rendering layers.
6.  **Are dataset metadata and lookup dictionaries fully separated?**
    **YES**. Lookup dictionary logic translates soil metrics, while metadata describes dataset provenance.
7.  **Are the proposed domain objects cohesive?**
    **YES**. Objects like `PhysicalProperties`, `ChemicalProperties`, and `HydrologicContext` own logically grouped parameters.
8.  **Is the architecture sufficiently generic for future soil datasets?**
    **YES**. Modularity in layer boundaries and property unit systems supports overlays of SoilGrids and national archives.
9.  **Can implementation begin without further architectural redesign?**
    **YES**. The mapping definitions and architectural models are finalized.

### Recommendation
With all nine checklist questions resolved as **YES**, we recommend freezing the scientific architecture and initiating the implementation phase for the remaining domain properties and schemas.
