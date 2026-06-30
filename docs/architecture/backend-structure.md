# Backend Project Structure: Global Soil Explorer

---

## Purpose
This document defines the logical project structure, module responsibilities, and dependency rules of the Global Soil Explorer backend service. It translates the high-level system architecture into a clear software organizational design, ensuring developers and AI assistants implement code in consistent, decoupled modules.

---

## Design Principles
1.  **Strict Dependency Direction**: Dependencies must flow inwards. Higher-level orchestration services depend on domain models and utilities, but the core domain models must have zero external dependencies.
2.  **Strict Separation of Concerns**: Each module has a specific, non-overlapping responsibility (e.g., separating offline preprocessing pipelines from runtime querying).
3.  **De-coupled Data Access**: Database logic is isolated from domain and application services, preventing storage schemas from leaking into business logic.
4.  **Fail-Safe Processing**: Error checking occurs at boundary interfaces, preventing corrupted states from entering core processing stages.

---

## Module Responsibilities

### 1. Application Services
*   **Purpose**: Handle incoming queries, coordinate processing, and return structured payloads.
*   **Responsibilities**: Validate request parameters, manage operation sequences, serialize domain output, and handle runtime exceptions.
*   **Dependencies**: Spatial Lookup, Soil Domain, Data Access, Configuration, Shared Utilities.
*   **What it owns**: Service controllers, request validators, response formatters, and exception mapping.
*   **What it must not own**: Spatial file indexing, raw database queries, and data transformation rules.

### 2. Spatial Lookup
*   **Purpose**: Resolve geographical coordinates to spatial index keys.
*   **Responsibilities**: Translate geographic coordinates to raster cell offsets and extract mapping unit values from the index grid.
*   **Dependencies**: Configuration, Shared Utilities.
*   **What it owns**: Grid coordinate calculations and binary stream offset parsing.
*   **What it must not own**: Attribute databases, classification dictionaries, and domain objects.

### 3. Soil Domain
*   **Purpose**: Define core soil science models and validation rules.
*   **Responsibilities**: Structure entities (`SoilProfile`, `SoilLayer`, `SoilProperty`, `SoilClassification`, `SoilComponent`) and enforce domain validation.
*   **Dependencies**: None (should remain independent of all other modules).
*   **What it owns**: Domain entity structures, validation logic, and profile sorting rules.
*   **What it must not own**: Spatial lookup math, database engines, and serialization codecs.

### 4. Data Access
*   **Purpose**: Manage all interactions with relational storage.
*   **Responsibilities**: Query mapping units, retrieve soil layers, and resolve integer codes using dictionary lookups.
*   **Dependencies**: Soil Domain, Configuration, Shared Utilities.
*   **What it owns**: Database connections, SQL queries, and mapping raw query rows to domain models.
*   **What it must not own**: Spatial coordinates, endpoint definitions, and ingestion scripting.

### 5. Dataset Processing
*   **Purpose**: Ingest and preprocess raw soil datasets offline.
*   **Responsibilities**: Validate raw data integrity, perform database normalization, build optimized spatial indexes, and cache staging files.
*   **Dependencies**: Configuration, Shared Utilities.
*   **What it owns**: Ingestion scripts, database creation pipelines, and validation tools.
*   **What it must not own**: Runtime coordinate lookups and API response formatting.

### 6. Configuration
*   **Purpose**: Manage global settings, environmental parameters, and path variables.
*   **Responsibilities**: Load environment settings, provide system path configurations, and export database credentials.
*   **Dependencies**: None.
*   **What it owns**: Config maps, file paths, and environment variable loaders.
*   **What it must not own**: Runtime data and domain business rules.

### 7. Shared Utilities
*   **Purpose**: Provide common helper functions across the backend.
*   **Responsibilities**: Provide mathematical utilities, coordinate parsers, and custom logging services.
*   **Dependencies**: None.
*   **What it owns**: Logging decorators, string formatters, and geographic math utilities.
*   **What it must not own**: Core database schemas, domain entities, and request handlers.

### 8. Testing
*   **Purpose**: Provide automated test coverage for all backend logic.
*   **Responsibilities**: Run unit tests, execute integration tests, and provide mock datasets.
*   **Dependencies**: All modules.
*   **What it owns**: Test suites, test runners, mock database definitions, and test coordinate indexes.
*   **What it must not own**: Production data and active deployment paths.

---

## Dependency Rules

To prevent coupling and maintain structural maintainability, the following dependency constraints are strictly enforced:

```text
  Application Services
      ↓ (depends on)
  Spatial Lookup, Data Access, Soil Domain, Configuration, Shared Utilities
  
  Data Access
      ↓ (depends on)
  Soil Domain, Configuration, Shared Utilities
  
  Spatial Lookup / Dataset Processing
      ↓ (depends on)
  Configuration, Shared Utilities
```

*   **Soil Domain** has **no dependencies** on other modules.
*   **Spatial Lookup** can only depend on **Configuration** and **Shared Utilities**.
*   **Data Access** depends on **Soil Domain**, **Configuration**, and **Shared Utilities**.
*   **Dataset Processing** depends on **Configuration** and **Shared Utilities**.
*   **Application Services** depends on **Spatial Lookup**, **Soil Domain**, **Data Access**, **Configuration**, and **Shared Utilities**.
*   **Shared Utilities** and **Configuration** have **no dependencies** on other logical modules.

---

## Data Flow Through the Backend

The execution data flow for resolving coordinate lookups follows these steps:

1.  **Request Entry**: The `Application Services` module receives a coordinate query.
2.  **Input Validation**: `Application Services` checks the parameter structure and formats coordinates.
3.  **Spatial Resolution**: `Application Services` invokes the `Spatial Lookup` module, which parses the spatial grid index and extracts the Mapping Unit Key.
4.  **Attribute Querying**: `Application Services` passes the Key to the `Data Access` module.
5.  **Data Retrieval**: `Data Access` queries the normalized database, resolves property codes against dictionary lookup tables, and maps raw rows into `SoilDomain` structures (e.g., layers, components).
6.  **Profile Compilation**: `Application Services` aggregates the returned domain entities, stacks the layers vertically by depth, and creates a unified `SoilProfile` domain object.
7.  **Response Construction**: `Application Services` serializes the `SoilProfile` and returns the final response.

---

## Extension Strategy
*   **Adding a New Soil Dataset**:
    Create a new schema migration script in `Dataset Processing` to normalize the new dataset's attributes. In `Data Access`, write a dataset-specific data retrieval adapter that implements a standard retrieval interface. The new adapter returns standardized `SoilProfile` domain objects, ensuring the rest of the application remains unchanged.
*   **Adding a New Service**:
    Define the service request/response domain models in `Soil Domain`. Write the query operations in `Data Access`. Create the request controllers in `Application Services`. The new service is added without modifying the boundaries of the spatial lookup engine or preprocessing pipeline.

---

## Risks
*   **Leaky Domain Boundaries**: Database concepts leaking into the `Soil Domain` layer, causing domain entities to mirror specific table schemas.
*   **Performance Gaps**: Inefficient seeking inside the raw spatial binary grid leading to slow lookup times.
*   **Circular Dependencies**: Importing orchestrator services inside domain models, which will break the dependency tree.
*   **Coupling to Testing**: Hardcoding test data configurations inside production modules rather than loading them dynamically in the `Testing` module.
