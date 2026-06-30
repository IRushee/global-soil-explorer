# System Architecture: Global Soil Explorer

---

## Purpose
This document defines the conceptual system architecture of the Global Soil Explorer. It serves as a technology-agnostic structural blueprint mapping out key subsystems, core components, and data flows. By separating logical boundaries from specific databases, servers, and frameworks, this architecture ensures the system remains maintainable, extensible, and stable over time.

---

## Architectural Goals
1.  **Simplicity**: Avoid unnecessary abstraction. Ensure the system components are easy to understand, inspect, and debug.
2.  **Maintainability**: Separate spatial calculations, data storage, and visual presentation so changes to one component do not affect the others.
3.  **Scientific Correctness**: Ensure data integrity and provenance are preserved. The system must represent physical and chemical soil properties exactly as documented in the source datasets.
4.  **Dataset Independence**: Design core domain layers to be independent of any single dataset structure, allowing future datasets to be integrated by returning a standard soil observation.
5.  **Extensibility**: Provide defined extension points to support future features like AI analytics, time-series data, and remote sensing.
6.  **Performance**: Optimize the data flow to ensure near-instantaneous spatial coordinate lookups and profile rendering.
7.  **Reproducibility**: Ensure all preprocessing and database transformation pipelines are scripted, deterministic, and repeatable.

---

## System Overview
The Global Soil Explorer is conceptually divided into three decoupled subsystems:

1.  **Ingestion & Preprocessing Subsystem**: Runs offline. It ingests raw, immutable datasets, runs validation checks, converts tabular database structures, and extracts spatial binary grids to generate runtime assets.
2.  **Core Query & Domain Subsystem**: Runs at runtime. It intercepts coordinate queries, resolves spatial identifiers, retrieves properties, and assembles them into structured, immutable soil observations.
3.  **Presentation Subsystem**: Runs on the client side. It provides an interactive map interface, captures coordinate selections, and visualizes vertical soil profile parameters.

---

## Core Components

### 1. User Interface (Interfaces / presentation)
*   **Purpose**: Provide an interactive graphical dashboard for soil exploration.
*   **Responsibilities**: Render global soil layers, handle map interactions, capture selected coordinates, and display vertical soil profile charts and metadata legends.
*   **Inputs**: Visual map layer data, structured Soil Observation payloads.
*   **Outputs**: Coordinate query coordinates.
*   **What it owns**: Visual layout state, client-side map interactions, charting components.
*   **What it must not own**: Spatial calculations, database queries, dataset dictionaries, and code translation logic.

### 2. Application Layer (Orchestration)
*   **Purpose**: Coordinate request execution and manage the sequence of operations.
*   **Responsibilities**: Receive coordinate queries, trigger the spatial lookup, coordinate database repository queries, and compile domain observations.
*   **Inputs**: Coordinate queries.
*   **Outputs**: Structured Soil Observation objects.
*   **What it owns**: Query orchestration, session flow.
*   **What it must not own**: Raw database connections and UI rendering.

### 3. Spatial Lookup Service
*   **Purpose**: Resolve geographical coordinates to spatial identifiers.
*   **Responsibilities**: Resolves a validated Coordinate into a dataset-specific spatial identifier.
*   **Inputs**: Validated coordinates.
*   **Outputs**: Spatial Identifier (opaque token or unit key).
*   **What it owns**: Spatial coordinate resolution logic.
*   **What it must not own**: Soil attribute databases, dictionary translations, and map presentation code.

### 4. Soil Domain Layer
*   **Purpose**: Model the scientific entities and rules of the soil science domain.
*   **Responsibilities**: Structure and validate geographic observations, profiles, layers, classifications, and properties. Provides an immutable business model.
*   **Inputs**: Raw database records and code-translation metadata.
*   **Outputs**: Validated domain objects (e.g., `SoilObservation`).
*   **What it owns**: Soil domain validation logic, vertical profile stacking order, and unit conversions.
*   **What it must not own**: File path routing, SQL query strings, and serialized response formats.

### 5. Repository Layer (Data Access)
*   **Purpose**: Retrieve database attributes and map them to domain models.
*   **Responsibilities**: Retrieves fully constructed SoilObservation domain objects, hides storage implementation details, and maps storage records into domain models.
*   **Inputs**: Dataset-specific spatial identifier.
*   **Outputs**: Fully constructed domain objects (e.g., `SoilObservation`).
*   **What it owns**: Query structures and domain mapping/construction logic.
*   **What it must not own**: Spatial coordinate lookups and API endpoint routing.

### 6. Offline Dataset Preprocessing Subsystem (Processing)
*   **Purpose**: Transform raw datasets into standardized internal representations. Runs strictly offline.
*   **Responsibilities**: Perform archive extraction (if required), validate raw structures, verify metadata, convert raw databases into query-optimized formats, and generate runtime assets. Does not participate in runtime queries.
*   **Inputs**: Raw read-only datasets and schemas.
*   **Outputs**: Optimized SQLite database and extracted binary raster files.
*   **What it owns**: Archive extraction tools, transformation scripts, and schema migration pipelines.
*   **What it must not own**: Runtime user queries and client presentation state.

---

## Dependency Direction

To maintain separation of concerns and ensure the domain model remains completely independent of database technologies, network frameworks, and routing packages, dependencies flow strictly inwards:

```text
  Interfaces
      ↓
  Application
      ↓
  Contracts
      ↓
  Infrastructure
```

*   **Domain**: The immutable scientific business model. Represents the central independent layer with **zero external dependencies** on other modules or layers.
*   **Contracts**: Defines abstractions. Depends strictly on **Domain**.
*   **Infrastructure**: Implements database and lookup interfaces defined in Contracts. Depends on **Contracts** and **Domain**.
*   **Application**: Orchestrates request processing workflows. Depends on **Contracts** and **Domain**.
*   **Interfaces**: The entry point (API endpoints, controllers). Depends on **Application** (and indirectly on Contracts/Domain).

---

## Runtime Data Assets
The runtime query system relies on a set of generated or pre-packaged files. These assets are prepared during the offline preprocessing phase and remain read-only at runtime:

1.  **Binary Raster (`.bil`)**
    *   **Purpose**: Stores the spatial grid mapping cell coordinates to spatial identifiers.
    *   **Lifecycle**: Extracted from a compressed archive (if distributed compressed) during offline preprocessing. Read directly at runtime.
    *   **Rationale**: Raster pixels remain outside SQLite to preserve efficient spatial lookup and avoid duplicating raster data.
2.  **Header File (`.hdr`)**
    *   **Purpose**: Stores metadata about the binary raster grid (dimensions, cell size, data type, byte order).
    *   **Lifecycle**: Read during preprocessing to validate coordinates and during runtime to calculate pixel offsets.
3.  **Projection File (`.prj`)**
    *   **Purpose**: Defines the Coordinate Reference System (CRS) of the raster grid (WGS 84).
    *   **Lifecycle**: Primarily used during preprocessing and dataset validation. Runtime components assume coordinates are already expressed in the expected CRS.
4.  **SQLite Database**
    *   **Purpose**: Stores relational attribute tables (e.g., layers, property definitions) and translation dictionaries, mapping spatial identifiers to classifications and values.
    *   **Lifecycle**: Generated offline. Queried at runtime.

---

## Runtime Asset Lifecycle

To ensure optimal performance and clarity for developers, the lifecycle of the system's data assets is strictly divided into distinct phases:

### 1. Distribution Phase
*   The raw dataset (such as HWSD v2.0) is typically distributed as a compressed archive containing binary raster grids and relational attribute tables.

### 2. Preprocessing Phase (Offline Pipeline)
*   **Archive Extraction**: If the dataset is distributed compressed, extraction occurs exactly once as part of the offline pipeline.
*   **Asset Ingestion**: Relational attribute tables are converted and migrated into an optimized SQLite database.
*   **No Raster Import**: Raster pixels are **never imported into SQLite** to preserve efficient spatial lookup and avoid duplicating raster data.
*   **Verification**: Row-counts, cell coordinates, and metadata are validated offline to generate runtime-ready assets.

### 3. Query Runtime Phase (Online Server)
*   **Direct Raster Read**: The query engine always operates on the extracted binary raster file, resolving coordinate positions directly from disk for high-performance lookup.
*   **Metadata Reference**: The header and projection files verify spatial boundaries.
*   **Attribute Retrieval**: The SQLite database is used solely to store and query normalized attribute data (layers, properties, taxonomic classifications).

---

## Runtime Lookup Pipeline

The logical architecture of the query pipeline describes abstract components only:

```text
  Coordinate
      ↓
  Application
      ↓
  SpatialLookupService
      ↓
  SoilObservationRepository
      ↓
  Domain Mapping
      ↓
  SoilObservation
```

1.  **Coordinate**: Query begins with a geographic `Coordinate` domain object.
2.  **Application**: Coordinates request execution, invoking the SpatialLookupService and SoilObservationRepository.
3.  **SpatialLookupService**: Resolves the geographical `Coordinate` into a dataset-specific spatial identifier.
4.  **SoilObservationRepository**: Retrieves the raw data associated with the spatial identifier, hiding storage implementation details.
5.  **Domain Mapping**: Processes the raw storage records and maps them into validated domain value objects.
6.  **SoilObservation**: Compiles the mapped domain objects into a single, cohesive, validated `SoilObservation` package.

### Current HWSD Runtime Implementation

For the HWSD v2.0 dataset, the logical pipeline is implemented using a binary raster grid and SQLite:

```text
  Coordinate
      ↓
  SpatialLookupService
      ↓
  HWSD BIL Raster
      ↓
  Spatial Identifier
      ↓
  SQLite Repository
      ↓
  Domain Mapping
      ↓
  SoilObservation
```

---

## Non-Goals
*   **Desktop GIS**: The project is not intended to become a full-featured desktop GIS client (like QGIS or ArcGIS) supporting complex spatial processing, custom map projection editing, or raw geodatabase authorship.
*   **Dataset Editor**: The system is read-only; it is not designed to edit, create, or alter soil inventory values.
*   **Raw Preprocessing Application**: The tool is not a general-purpose converter for raw spatial files outside the scope of target soil datasets.
*   **Replacement for Scientific Databases**: It does not replace the master repositories hosted by institutions (FAO, IIASA, ISRIC) and remains a presentation and discovery tool.
