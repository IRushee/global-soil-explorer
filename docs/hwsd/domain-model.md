# Domain Model: Global Soil Explorer

---

## Document Metadata
*   **Purpose**: Define the conceptual domain model and core objects of the Global Soil Explorer application, focusing strictly on soil science concepts and workflows.
*   **Audience**: Product owners, backend developers, UI/UX designers, and scientific advisors.
*   **Assumptions**:
    *   The model must remain storage-agnostic and dataset-independent, representing the universal physical reality of soil properties.
    *   Since the domain is read-only and immutable at runtime, all domain concepts are modeled as Value Objects with no state transitions or aggregate root lifecycles.

---

## 1. Core Domain Objects

### 1. `Coordinate` (Value Object)
*   **Purpose**: Represents a specific spatial point on the Earth's surface.
*   **Responsibilities**: Defines the geographic location queried by the user (implicitly assuming the WGS 84 coordinate system).
*   **Important Attributes**:
    *   Latitude (Decimal Degrees North/South)
    *   Longitude (Decimal Degrees East/West)
*   **Relationships**: Contained within a `SoilObservation`.
*   **Source in HWSD**: User query inputs / CRS parameters in `HWSD2.prj`.
*   **Mapping Type**: Verified

### 2. `SoilObservation` (Value Object)
*   **Purpose**: Represents the complete snapshot of soil characteristics observed at a specific geographic point.
*   **Responsibilities**: Acts as the immutable data package returned by a coordinate query.
*   **Important Attributes**:
    *   Location identifier (derived from coordinate values)
    *   Land/Water status indicator
*   **Relationships**: Contains a single `Coordinate` and an ordered list of one or more `SoilProfile` objects.
*   **Source in HWSD**: Calculated by resolving coordinates to cell indices in `HWSD2.bil` and querying associated records.
*   **Mapping Type**: Verified

### 3. `SoilProfile` (Value Object)
*   **Purpose**: Represents a distinct, vertically layered soil type.
*   **Responsibilities**: Stacks vertical layers and couples them with taxonomic classifications.
*   **Important Attributes**:
    *   Composition Share (Optional percentage weight representing how much of this profile makes up the location, from 0 to 100%. Nullable for qualitative datasets).
*   **Relationships**: Contained within a `SoilObservation`; has a single `SoilClassification`; contains an ordered list of `SoilLayers`.
*   **Source in HWSD**: Inferred by grouping layers in `HWSD2_LAYERS` (where share maps to the database component `SHARE` value).
*   **Mapping Type**: Inferred

### 4. `SoilLayer` (Value Object)
*   **Purpose**: Represents a specific vertical depth interval of a `SoilProfile`.
*   **Responsibilities**: Holds physical and chemical properties measured within a specific depth slice.
*   **Important Attributes**:
    *   Layer Code (e.g., D1 to D7)
    *   Top Boundary Depth (cm)
    *   Bottom Boundary Depth (cm)
*   **Relationships**: Contained within a `SoilProfile`; contains multiple `SoilProperties`.
*   **Source in HWSD**: Individual rows in `HWSD2_LAYERS` corresponding to `LAYER` variables.
*   **Mapping Type**: Verified

### 5. `SoilProperty` (Value Object)
*   **Purpose**: Represents a specific physical, chemical, or organic attribute of a `SoilLayer`.
*   **Responsibilities**: Stores the scientific value and its unit of measure.
*   **Important Attributes**:
    *   Property Type (represented as PropertyType enum, e.g., pH, Organic Carbon, Sand Fraction)
    *   Value (Numeric float value)
    *   Unit (represented as Unit enum, e.g., percent, g/cm3, pH)
*   **Relationships**: Measured within a `SoilLayer`.
*   **Source in HWSD**: Column values in `HWSD2_LAYERS` and metadata definitions in `HWSD2_LAYERS_METADATA`.
*   **Mapping Type**: Verified

### 6. `SoilClassification` (Value Object)
*   **Purpose**: Represents the scientific classification category of a soil component.
*   **Responsibilities**: Standardizes soil naming and references across international and national taxonomic standards.
*   **Important Attributes**:
    *   Taxonomy standard (e.g., WRB 2022, FAO 1990)
    *   Class Symbol (Abbreviation code)
    *   Class Name (Resolved descriptive label)
*   **Relationships**: Classifies a `SoilProfile`.
*   **Source in HWSD**: Attribute codes in `HWSD2_LAYERS`/`HWSD2_SMU` mapped to `D_*` lookup tables.
*   **Mapping Type**: Verified

---

## 2. Domain Relationships

Conceptually, the domain objects connect in a logical value-based hierarchy:

```text
  Coordinate
      ↓
  SoilObservation (Value Object container)
      ↓ (contains one or more)
  SoilProfile (with optional composition_share)
      ↓ (consists of)
  SoilLayer (ordered vertically)
      ↓ (contains)
  SoilProperty (acidity, texture, carbon, etc.) & SoilClassification
```

1.  A user provides a geographical **`Coordinate`**, which initiates a **`SoilObservation`**.
2.  A **`SoilObservation`** holds a list of one or more **`SoilProfiles`**. Each profile represents a share of the soil composition at that coordinate.
3.  Each **`SoilProfile`** is classified under a standard **`SoilClassification`** and consists of an ordered stack of **`SoilLayers`**.
4.  Each **`SoilLayer`** contains multiple physical and chemical **`SoilProperties`** measured within its specific top and bottom boundaries.

---

## 3. Open Design Questions

Before transitioning to database conversion and API endpoint design, the following domain concepts require product clarification:

1.  **Rendering Multiple Profiles**:
    *   Since a single coordinate query can yield multiple `SoilProfiles` (e.g., a mapping unit consisting of 60% Vertisol and 40% Luvisol), how should the interface present this? Should we display the dominant profile first, or let the user toggle between profiles via tabs?
2.  **Depth Profile Representation**:
    *   The raw data defines static depth intervals (e.g. 0-20 cm, 20-40 cm). If a user queries the soil properties at exactly 15 cm, should the model support interpolation (e.g., spline curves) or return the properties of the containing interval as a step-wise value?
3.  **National vs. Global Taxonomies**:
    *   The database contains both legacy FAO classifications, modern global WRB classifications, and sparse national classification codes. Which classification system takes priority when displaying the profile naming to the user?
4.  **Domain Representation of Unmeasured Attributes**:
    *   If a soil property (like electrical conductivity) is missing (`NULL` in database) for a specific depth layer, how should the domain model represent this? (e.g. indicating it as "Unmeasured/Data Gap" vs. omitting the property from the layer's output list).
