# API Specification: Global Soil Explorer

---

## Purpose
This document defines the public capabilities of the Global Soil Explorer. It acts as the functional boundary contract of the Orchestration Layer, detailing how external clients (such as the browser interface or secondary data clients) interact with the core soil query engine. By abstracting storage schemes and spatial file operations, the API provides a clean, unified gateway for soil data discovery and vertical profiling.

---

## Design Principles
1.  **Domain-First**: API request schemas and response structures correspond directly to standard soil science concepts (observations, profiles, layers) rather than underlying database table boundaries.
2.  **Dataset-Independent**: The payload structure is identical regardless of the target dataset (e.g., HWSD, SoilGrids, etc.) satisfying the query.
3.  **Storage-Independent**: The API contract is decoupled from active database engines, indexes, or file seek mechanisms, remaining unaffected by database migrations.
4.  **Stateless Requests**: Every request contains all necessary parameters to resolve itself, requiring no session history or server-side transaction states.
5.  **Predictable Responses**: Queries with identical coordinate inputs and dataset parameters yield identical results.
6.  **Explicit Error Reporting**: Failures (e.g., out-of-bounds queries, missing properties) return descriptive, structured error domains to guide client applications.
7.  **Versionable**: The contract is structured to accommodate additive enhancements without breaking existing client integrations.

---

## Core Services

### 1. Coordinate Lookup
*   **Purpose**: Resolve a geographical coordinate point to its spatial index location.
*   **Inputs**:
    *   Coordinates (latitude and longitude)
*   **Outputs**:
    *   Location Index Key
*   **Domain Objects Involved**: `Coordinate`, `SoilObservation`.
*   **Preconditions**: Coordinates must represent valid geographical locations.
*   **Failure Conditions**: The coordinate lands outside supported dataset boundaries or on unmapped territory (e.g., oceans or glaciers), returning a "No Soil Data" error.

### 2. Soil Profile Retrieval
*   **Purpose**: Fetch the complete vertical soil profiles observed at a location.
*   **Inputs**:
    *   Location Index Key
    *   Dataset Version / Name (Optional, defaults to active standard)
*   **Outputs**:
    *   Complete `SoilObservation` containing the coordinates and a list of vertically stacked `SoilProfile` objects.
*   **Domain Objects Involved**: `SoilObservation`, `SoilProfile`, `SoilLayer`, `SoilProperty`, `SoilClassification`.
*   **Preconditions**: The requested Location Index Key must exist in the active dataset index.
*   **Failure Conditions**: The Location Index Key is invalid or missing, returning a "No Soil Data" or "Invalid Key" error.

### 3. Soil Property Query
*   **Purpose**: Query specific physical or chemical soil attributes at a location or within a depth range.
*   **Inputs**:
    *   Coordinates (latitude and longitude)
    *   Property name key (e.g., pH, Organic Carbon)
    *   Depth interval boundaries (Optional)
*   **Outputs**:
    *   Specific property value and unit of measure.
*   **Domain Objects Involved**: `Coordinate`, `SoilLayer`, `SoilProperty`.
*   **Preconditions**: Coordinates must reside within valid mapping unit bounds, and the property key must be supported.
*   **Failure Conditions**: The property key is unrecognized, or the depth interval exceeds valid soil depth ranges.

### 4. Soil Classification Query
*   **Purpose**: Resolve scientific soil codes to human-readable taxonomy names and descriptions.
*   **Inputs**:
    *   Soil classification code
    *   Taxonomy standard (e.g., WRB 2022, FAO 1990)
*   **Outputs**:
    *   Resolved standard name, qualifier description, and rendering color codes.
*   **Domain Objects Involved**: `SoilClassification`.
*   **Preconditions**: The classification code must exist within the target taxonomy catalog.
*   **Failure Conditions**: Unrecognized code or unsupported taxonomy standard.

### 5. Dataset Metadata
*   **Purpose**: Retrieve metadata regarding loaded datasets, version histories, and spatial boundaries.
*   **Inputs**:
    *   Dataset identifier key
*   **Outputs**:
    *   `DatasetMetadata` detailing spatial resolution, coordinate system, citations, and licenses.
*   **Domain Objects Involved**: `DatasetMetadata`.
*   **Preconditions**: The target dataset must be loaded in the repository.
*   **Failure Conditions**: Dataset identifier is unrecognized or inactive.

### 6. Search & Discovery
*   **Purpose**: Search for Location observations by regional descriptors, climate zone, or dominant classification symbol.
*   **Inputs**:
    *   Search text query
    *   Filters (e.g., dominant soil group, climate zone)
*   **Outputs**:
    *   List of matching Soil Observations, composition shares, and their spatial coordinates.
*   **Domain Objects Involved**: `SoilObservation`, `SoilClassification`.
*   **Preconditions**: Search queries must be alphanumeric.
*   **Failure Conditions**: No matches found, or filter arguments are malformed.

### 7. Health & Capability Information
*   **Purpose**: Query system capability parameters, supported versions, and operational health.
*   **Inputs**: None.
*   **Outputs**: Operational health status, supported API versions, and active dataset listings.
*   **Domain Objects Involved**: None.
*   **Preconditions**: None.
*   **Failure Conditions**: Internal service failure preventing operational status checks.

---

## Common Domain Objects

The services exchange the following conceptual domain objects:
*   **`Coordinate`**: Geographic spatial reference values (latitude, longitude).
*   **`SoilObservation`**: Geographic query wrapper carrying coordinate values and a list of observed profiles.
*   **`SoilProfile`**: Vertically stacked sequence of layers and classification qualifiers, containing an optional composition share parameter.
*   **`SoilLayer`**: Specified vertical depth segment boundaries (top and bottom limits in cm).
*   **`SoilProperty`**: Individual physical or chemical attribute (property type, value, unit of measure).
*   **`SoilClassification`**: Standardized taxonomic classification names and description labels.
*   **`DatasetMetadata`**: Structural details of the source inventory (version, license, coordinate reference system, and scale).

---

## Error Model

When a service fails, the Orchestration Layer returns a structured error payload detailing:
*   **Invalid Coordinate**: The coordinates are out of bounds (Latitude $> 90^\circ$ or Longitude $> 180^\circ$) or non-numeric.
*   **No Soil Data**: The coordinates are valid but land on oceans, glaciers, or unmapped territory.
*   **Unsupported Dataset**: The requested dataset version is not loaded in the system.
*   **Internal Processing Error**: Database query failures, file read timeouts, or ingestion errors prevent request resolution.

---

## Versioning Strategy
To ensure client stability as the platform evolves:
*   **Service Versioning**: The service API is versioned with major-minor identifiers. Bumping the major version indicates breaking changes to payloads. Minor versions represent additive enhancements (new optional parameters or helper attributes).
*   **Dataset Versioning**: Dataset attributes (such as classifications and properties) are tagged with the source dataset version inside `DatasetMetadata`, allowing clients to request and handle different editions of the scientific inventories concurrently.

---

## Future Services
*   **Multi-Dataset Comparison**: Simultaneously request and compare soil properties from different data sources (e.g. HWSD vs. SoilGrids) for the same coordinates.
*   **AI Interpretation**: Generate natural language explanations and suitability summaries for a queried soil profile.
*   **Bulk Coordinate Queries**: Submit a list of coordinate coordinates to retrieve a combined array of matching profiles.
*   **Area Statistics**: Query customized polygon boundaries to retrieve aggregate soil profiles (means, medians, variances) across that region.
*   **Export Services**: Extract and download queried soil profiles in standard geographic data packages.

---

## Traceability
*   **Domain Model**: All domain exchange objects (`SoilObservation`, `SoilProfile`, `SoilLayer`, `SoilProperty`, `SoilClassification`, `Coordinate`) map directly to the conceptual entities defined in `docs/hwsd/domain-model.md`.
*   **System Architecture**: The core services correspond to components in the Orchestration Layer and Data Access Layer as outlined in `docs/architecture/system-architecture.md`.
