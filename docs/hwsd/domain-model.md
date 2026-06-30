# Domain Model: Global Soil Explorer

---

## Document Metadata
*   **Purpose**: Define the conceptual domain model and core objects of the Global Soil Explorer application, focusing strictly on soil science concepts and workflows.
*   **Audience**: Product owners, backend developers, UI/UX designers, and scientific advisors.
*   **Assumptions**:
    *   The model must remain storage-agnostic, representing real-world soil objects rather than relational database tables or API formats.

---

## 1. Core Domain Objects

### 1. `Coordinate`
*   **Purpose**: Represents a specific spatial point on the Earth's surface.
*   **Responsibilities**: Defines the location searched or clicked by the user.
*   **Important Attributes**:
    *   Latitude (Decimal Degrees North/South)
    *   Longitude (Decimal Degrees East/West)
    *   Coordinate System (e.g., WGS 84)
*   **Relationships**: Resolves to a single `SoilLocation`.
*   **Source in HWSD**: User query inputs / CRS parameters in `HWSD2.prj`.
*   **Mapping Type**: Verified

### 2. `SoilLocation`
*   **Purpose**: Represents a localized geographic grid cell containing soil properties.
*   **Responsibilities**: Links a geographical coordinate to its underlying soil classification mapping unit.
*   **Important Attributes**:
    *   Grid Coordinates (Row, Column)
    *   Spatial Area (Bounding box of the grid cell)
    *   No-Data Status (Boolean flag indicating if the location represents water or unmapped land)
*   **Relationships**: Located at a `Coordinate`; mapped to a single `SoilMappingUnit`.
*   **Source in HWSD**: Spatial raster file `HWSD2.bil` and cell definitions in `HWSD2.hdr`.
*   **Mapping Type**: Verified

### 3. `SoilMappingUnit`
*   **Purpose**: Represents a geographical association of soils that share similar landscape characteristics.
*   **Responsibilities**: Group multiple components, defining the dominant soil classification and climate constraints of the region.
*   **Important Attributes**:
    *   Unit Identifier (Global Map Unit Key)
    *   Dataset Source (Lineage of the local input inventory)
    *   Climate Class (Koppen-Geiger climate classification)
*   **Relationships**: Mapped to multiple `SoilLocations`; contains one or more `SoilComponents`.
*   **Source in HWSD**: `HWSD2_SMU` table.
*   **Mapping Type**: Verified

### 4. `SoilComponent`
*   **Purpose**: Represents a distinct soil type that occupies a portion of a `SoilMappingUnit`.
*   **Responsibilities**: Stores the properties and classification of a specific soil variety within a mapping unit.
*   **Important Attributes**:
    *   Sequence Number (Rank or priority within the Mapping Unit)
    *   Share Percentage (Spatial coverage fraction of the Mapping Unit, from 0 to 100%)
    *   Rooting Constraints (Maximum rootable depth limits)
    *   Drainage Behavior (Reference drainage class)
*   **Relationships**: Belongs to a single `SoilMappingUnit`; has a single `SoilClassification`; contains a single `SoilProfile`.
*   **Source in HWSD**: `HWSD2_LAYERS` table (grouped by `SEQUENCE` and `SHARE`).
*   **Mapping Type**: Verified

### 5. `SoilProfile`
*   **Purpose**: Represents the full vertical sequence of soil layers for a specific `SoilComponent`.
*   **Responsibilities**: Collects and sequences soil layers from the surface down to the parent rock.
*   **Important Attributes**:
    *   Total Depth (cm)
    *   Layer Count
*   **Relationships**: Belongs to a single `SoilComponent`; consists of an ordered sequence of `SoilLayers`.
*   **Source in HWSD**: Conceptually derived by grouping layers in `HWSD2_LAYERS`.
*   **Mapping Type**: Inferred

### 6. `SoilLayer`
*   **Purpose**: Represents a specific vertical depth interval of a `SoilProfile`.
*   **Responsibilities**: Holds physical and chemical properties measured within a specific depth slice.
*   **Important Attributes**:
    *   Layer Code (e.g., D1 to D7)
    *   Top Boundary Depth (cm)
    *   Bottom Boundary Depth (cm)
*   **Relationships**: Part of a `SoilProfile`; contains multiple `SoilProperties`.
*   **Source in HWSD**: Individual rows in `HWSD2_LAYERS` corresponding to `LAYER` variables.
*   **Mapping Type**: Verified

### 7. `SoilProperty`
*   **Purpose**: Represents a specific physical, chemical, or organic attribute of a `SoilLayer`.
*   **Responsibilities**: Stores the scientific value, unit of measure, and data quality flag.
*   **Important Attributes**:
    *   Name (e.g., pH, Organic Carbon, Sand Fraction)
    *   Value (Numeric or categorical code)
    *   Unit (e.g., %, g/cm3, dS/m)
*   **Relationships**: Measured within a `SoilLayer`.
*   **Source in HWSD**: Column values in `HWSD2_LAYERS` and metadata definitions in `HWSD2_LAYERS_METADATA`.
*   **Mapping Type**: Verified

### 8. `SoilClassification`
*   **Purpose**: Represents the scientific classification category of a soil component.
*   **Responsibilities**: Standardizes soil naming and references across international and national taxonomic standards.
*   **Important Attributes**:
    *   Taxonomy standard (e.g., WRB 2022, FAO 1990, National standards)
    *   Class Symbol (Abbreviation code)
    *   Class Name (Resolved descriptive label)
*   **Relationships**: Classifies a `SoilComponent` or `SoilMappingUnit`.
*   **Source in HWSD**: Attribute codes in `HWSD2_LAYERS`/`HWSD2_SMU` mapped to `D_*` lookup tables.
*   **Mapping Type**: Verified

---

## 2. Domain Relationships

Conceptually, the domain objects connect in a logical spatial-to-biological hierarchy:

```text
  Coordinate
      ↓
  SoilLocation
      ↓
  SoilMappingUnit
      ↓ (has one or more)
  SoilComponent
      ↓ (has one)
  SoilClassification & SoilProfile
                           ↓ (consists of)
                       SoilLayer (ordered vertically)
                           ↓ (contains)
                       SoilProperty (acidity, texture, carbon, etc.)
```

1.  A user provides a geographical **`Coordinate`**, which points to a specific grid-cell **`SoilLocation`**.
2.  A **`SoilLocation`** exists within a regional **`SoilMappingUnit`**.
3.  A **`SoilMappingUnit`** represents an association of distinct soils, containing one or more **`SoilComponents`**. Each component represents a share of the mapping unit's land area.
4.  Each **`SoilComponent`** is classified under a standard **`SoilClassification`** and possesses a unique **`SoilProfile`**.
5.  A **`SoilProfile`** represents a vertical stack of vertically ordered **`SoilLayers`**.
6.  Each **`SoilLayer`** contains multiple physical and chemical **`SoilProperties`** measured within its specific top and bottom boundaries.

---

## 3. Open Design Questions

Before transitioning to database conversion and API endpoint design, the following domain concepts require product clarification:

1.  **Rendering Multiple Components**:
    *   Since a single location query can yield multiple `SoilComponents` (e.g., a mapping unit consisting of 60% Vertisol and 40% Luvisol), how should the interface present this? Should we display a default "dominant component" profile first, or let the user choose between the components via tabs?
2.  **Depth Profile Representation**:
    *   The raw data defines static depth intervals (e.g. 0-20 cm, 20-40 cm). If a user queries the soil properties at exactly 15 cm, should the model support interpolation (e.g., spline curves) or return the properties of the containing interval as a step-wise value?
3.  **National vs. Global Taxonomies**:
    *   The database contains both legacy FAO classifications, modern global WRB classifications, and sparse national classification codes. Which classification system takes priority when displaying the profile naming to the user?
4.  **Domain Representation of Unmeasured Attributes**:
    *   If a soil property (like electrical conductivity) is missing (`NULL` in database) for a specific depth layer, how should the domain model represent this? (e.g. indicating it as "Unmeasured/Data Gap" vs. omitting the property from the layer's output list).
