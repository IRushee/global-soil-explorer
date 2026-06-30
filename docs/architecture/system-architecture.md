# System Architecture: Global Soil Explorer

---

## Purpose
This document defines the conceptual system architecture of the Global Soil Explorer. It serves as a technology-agnostic structural blueprint mapping out key subsystems, core components, and data flows. By separating logical boundaries from specific databases, servers, and frameworks, this architecture ensures the system remains maintainable, extensible, and stable over time.

---

## Architectural Goals
1.  **Simplicity**: Avoid unnecessary abstraction. Ensure the system components are easy to understand, inspect, and debug.
2.  **Maintainability**: Separate spatial calculations, data storage, and visual presentation so changes to one component do not affect the others.
3.  **Scientific Correctness**: Ensure data integrity and provenance are preserved. The system must represent physical and chemical soil properties exactly as documented in the source datasets.
4.  **Dataset Independence**: Design core domain layers to be independent of any single dataset structure (such as traditional mapping unit structures), allowing future datasets (including gridded predictions) to be integrated by returning a standard soil observation.
5.  **Extensibility**: Provide defined extension points to support future features like AI analytics, time-series data, and remote sensing.
6.  **Performance**: Optimize the data flow to ensure near-instantaneous spatial coordinate lookups and profile rendering.
7.  **Reproducibility**: Ensure all preprocessing and database transformation pipelines are scripted, deterministic, and repeatable.

---

## System Overview
The Global Soil Explorer is conceptually divided into three decoupled subsystems:

1.  **Ingestion & Preprocessing Subsystem**: Runs offline. It ingests raw, immutable datasets, runs validation checks, and compiles them into optimized spatial indexes and normalized attribute tables.
2.  **Core Query & Domain Subsystem**: Runs at runtime. It intercepts coordinate queries, converts coordinates to grid cell offsets, extracts spatial index keys, retrieves physical/chemical properties, and assembles them into structured soil observations.
3.  **Presentation Subsystem**: Runs on the client side. It provides an interactive map interface, captures coordinate selections, and visualizes vertical soil profile parameters.

---

## Core Components

### 1. User Interface (UI)
*   **Purpose**: Provide an interactive graphical dashboard for soil exploration.
*   **Responsibilities**: Render global soil layers, handle map interactions, capture selected coordinates, and display vertical soil profile charts and metadata legends.
*   **Inputs**: Visual map layer data, structured Soil Observation payloads.
*   **Outputs**: Coordinate query coordinates.
*   **What it owns**: Visual layout state, client-side map interactions, charting components.
*   **What it must not own**: Spatial calculations, database queries, dataset dictionaries, and code translation logic.

### 2. Orchestration Layer
*   **Purpose**: Coordinate request execution and manage the sequence of operations.
*   **Responsibilities**: Receive coordinate queries, trigger the spatial lookup, coordinate database attribute queries, and compile domain observations.
*   **Inputs**: Coordinate queries.
*   **Outputs**: Structured Soil Observation objects.
*   **What it owns**: Query orchestration, session flow.
*   **What it must not own**: Raw database connections, direct binary raster file seeks, and UI rendering.

### 3. Spatial Lookup Engine
*   **Purpose**: Resolve geographical coordinates to spatial index keys.
*   **Responsibilities**: Translate latitude/longitude coordinate values to raster grid offsets and extract pixel values.
*   **Inputs**: Validated coordinates.
*   **Outputs**: Spatial Index Key.
*   **What it owns**: Spatial boundary calculation formulas and grid offset algorithms.
*   **What it must not own**: Soil attribute databases, dictionary translations, and map presentation code.

### 4. Soil Domain Layer
*   **Purpose**: Model the scientific entities and rules of the soil science domain.
*   **Responsibilities**: Structure and validate geographic observations, profiles, layers, classifications, and properties.
*   **Inputs**: Raw database records and code-translation metadata.
*   **Outputs**: Validated domain objects (e.g., `SoilObservation`).
*   **What it owns**: Soil domain validation logic, vertical profile stacking order, and unit conversions.
*   **What it must not own**: File path routing, SQL query strings, and serialized output formats.

### 5. Data Access Layer
*   **Purpose**: Abstract query operations from the active storage databases.
*   **Responsibilities**: Retrieve soil database attribute records, retrieve vertical layer records, and perform joins against dictionary lookup tables.
*   **Inputs**: Spatial Index Key.
*   **Outputs**: Raw database records and resolved labels.
*   **What it owns**: Query structures, database retrieval logic.
*   **What it must not own**: Spatial grid logic, business rules, and application state.

### 6. Dataset Repository
*   **Purpose**: Store the authoritative dataset sources.
*   **Responsibilities**: Host raw datasets, version markers, and metadata schemas.
*   **Inputs**: Ingestion releases.
*   **Outputs**: Read-only raw data streams.
*   **What it owns**: Raw datasets, dataset versions, and dataset metadata.
*   **What it must not own**: Runtime caches, query logic, and derived products.

### 7. Data Processing Pipeline
*   **Purpose**: Transform raw datasets into standardized internal representations for querying.
*   **Responsibilities**: Read raw datasets, run structural validation, convert tables and grids to optimized internal structures, and cache standardized representations.
*   **Inputs**: Raw datasets and schemas from the Dataset Repository.
*   **Outputs**: Standardized spatial grids and query-optimized relational tables.
*   **What it owns**: Extraction scripts, transformation rules, indexing tools, and derived schemas.
*   **What it must not own**: Runtime queries, client state, and API routing.

### 8. Documentation & Knowledge Base
*   **Purpose**: Maintain consistency across the codebase and data structure.
*   **Responsibilities**: Define table schemas, attribute dictionaries, design records, and lookup workflows.
*   **Inputs**: System structure audits.
*   **Outputs**: System schemas, data specifications, and development rules.
*   **What it owns**: Markdown documentation suites, technical references, and soil terms dictionaries.
*   **What it must not own**: Executable code files and active databases.

---

## System Data Flow

The system processes a user's query in a linear, unidirectional data flow:

```text
  User
   ↓
  Map Interaction
   ↓
  Coordinate
   ↓
  Spatial Lookup
   ↓
  Domain Objects
   ↓
  Soil Observation
   ↓
  Presentation
```

1.  **User**: Interacts with the interface.
2.  **Map Interaction**: User triggers a geographical location query (by click or text entry).
3.  **Coordinate**: Represents the selected point on the Earth's surface.
4.  **Spatial Lookup**: The system extracts the location index key matching the coordinate.
5.  **Domain Objects**: The system retrieves the soil classifications, layers, and properties associated with the index.
6.  **Soil Observation**: Combines layers and properties into a unified, vertically ordered soil profile representation nested under a single geographic observation.
7.  **Presentation**: Renders the soil observation visually on the interface.

---

## Component Interactions
*   The **User Interface** captures coordinate selections and requests lookups from the **Orchestration Layer**.
*   The **Orchestration Layer** validates parameters and queries the **Spatial Lookup Engine**.
*   The **Spatial Lookup Engine** calculates cell coordinates, seeks the index in the **Data Processing Pipeline**'s generated spatial index, and returns the spatial index key to the **Orchestration Layer**.
*   The **Orchestration Layer** forwards this key to the **Data Access Layer**.
*   The **Data Access Layer** queries the normalized tables, joins the results against dictionary tables, and returns raw record sets.
*   The **Orchestration Layer** passes these records to the **Soil Domain Layer**, which translates them into structured **SoilObservation** domain objects containing a list of **SoilProfile** instances.
*   The **Orchestration Layer** formats this observation payload and returns it to the **User Interface** for presentation.

---

## Architectural Principles
*   **Separation of Concerns**: Distinct separation between presentation logic, coordinate translation, database querying, and scientific domain objects.
*   **Single Responsibility**: Each component has one job (e.g., the lookup engine converts coordinates to keys and nothing else).
*   **Domain-First Design**: The core business logic models soil science concepts (observations, profiles, layers) rather than storage layouts.
*   **Storage Independence**: The query and domain components are decoupled from storage technologies, allowing changes to databases without rewrite of business logic.
*   **Evidence-Based Processing**: Preprocessing steps validate outputs against raw source counts to prevent loss.
*   **Immutable Raw Datasets**: Original source data is read-only and never modified.
*   **Reproducibility**: Ingestion pipelines are automated to guarantee repeatability.

---

## Component Boundaries
*   The **Spatial Lookup Engine** owns spatial cell calculations but is unaware of database tables, column names, or client visual layouts.
*   The **Data Access Layer** owns database queries but is unaware of coordinate maps, pixel offsets, or UI charting tools.
*   The **User Interface** owns client interactions and chart layouts but is unaware of raw database queries, raster file seek logic, or dictionary codes.
*   The **Data Processing Pipeline** owns dataset transformations but does not handle runtime user queries or client state.

---

## Non-Goals
*   **Desktop GIS**: The project is not intended to become a full-featured desktop GIS client (like QGIS or ArcGIS) supporting complex spatial processing, custom map projection editing, or raw geodatabase authorship.
*   **Dataset Editor**: The system is read-only; it is not designed to edit, create, or alter soil inventory values.
*   **Raw Preprocessing Application**: The tool is not a general-purpose converter for raw spatial files outside the scope of target soil datasets.
*   **Replacement for Scientific Databases**: It does not replace the master repositories hosted by institutions (FAO, IIASA, ISRIC) and remains a presentation and discovery tool.

---

## Future Extension Points
1.  **Dataset Adapter**: A standardized interface enabling other soil inventories (such as DSMW, SoilGrids, OpenLandMap) to be adapted into the common domain model without modifying the application logic.
2.  **Derived Products**: Dedicated adapters to compute indices from raw soil properties:
    *   *Crop Suitability*: Predicting agricultural viability.
    *   *Carbon Estimates*: Soil carbon stock calculations.
    *   *Erosion Risk*: Vulnerability indexes.
    *   *Flood Susceptibility*: Soil water drainage assessment.
3.  **AI Assistants**: AI plugins can consume the standard `SoilObservation` domain models to provide automated regional agricultural reports or ecological commentary.
4.  **Spatial Analysis**: High-performance spatial analysis modules (such as bounding-box aggregators) can hook directly into the Data Access Layer.
5.  **Time-Series Data**: The `SoilObservation` object can be extended to include historical timestamps, tracking carbon changes over time.
6.  **Remote Sensing**: Surface parameters from satellite data can be joined with mapping units to provide land cover overlays.
7.  **User Annotations**: Crowd-sourced soil observations can be linked to mapping unit identifiers.
8.  **Plugins**: A standardized calculations interface allows adding custom predictors (e.g., crop suitability algorithms) without modifying core code.
9.  **Export Formats**: Serialization modules (GeoJSON, Shapefile, CSV) can be added to the Orchestration Layer to output data in alternative formats.

---

## Risks and Unknowns

### Verified
*   Raster layout metadata (dimensions of $21,600 \times 43,200$) is stable.
*   The spatial index key acts as the join field linking the spatial grid to the relational database tables in the processing/repository layer.
*   Dictionary tables are essential to resolve code integers to text values.

### Assumed
*   GPS coordinates received from the map client align with the unprojected WGS 84 spatial index without cell edge offset errors.
*   The core dataset has no orphan mapping unit keys.

### Unknown (Architectural Questions)
*   **Multiple Dataset Reconciliation**: How to reconcile conflicting reference boundaries and classification grids when layering multiple soil inventories.
*   **Dataset Versioning**: Structuring migration pipelines when source datasets release updates.
*   **Incomplete Soil Profiles**: Resolving spatial regions where specific depth intervals have null or unmeasured property values.
*   **Spatial Precision Guarantees**: Managing coordinate rounding errors when mapping continuous GPS locations to discrete grid cell boundaries.
*   **Soil Composition Representation**: Handling observations where the sum of profile composition shares does not equal 100%.

---

## Traceability
*   **Dataset Inventory**: Informs the file structures managed by the **Dataset Repository**.
*   **Database Discovery**: Outlines the schema metadata and lookup indexes managed by the **Data Access Layer**.
*   **Schema Analysis & Attribute Dictionary**: Defines the entities, data types, and values modeled by the **Soil Domain Layer**.
*   **Lookup Workflow**: Modeled by the **System Data Flow** and **Component Interactions** sections.
