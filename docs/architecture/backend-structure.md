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

### 1. Interfaces
*   **Purpose**: Provide entry points into the application.
*   **Responsibilities**: Translate external client requests into application service commands and present results (e.g. web controllers, CLI tools).
*   **Dependencies**: Orchestration Layer, Contracts, Shared Utilities, Configuration.
*   **What it owns**: Routing configurations, CLI command parsers, input formatters.
*   **What it must not own**: Business logic workflows, database access, and spatial seeking.

### 2. Application Services (Orchestration)
*   **Purpose**: Coordinate business workflows and request flows.
*   **Responsibilities**: Coordinate lookup and query processing sequences, invoke spatial translation, and manage transactions.
*   **Dependencies**: Spatial Lookup, Soil Domain, Data Access, Configuration, Shared Utilities, Contracts.
*   **What it owns**: Orchestration services, workflow coordinators.
*   **What it must not own**: Database connections, direct spatial raster seeking, and web routing.

### 3. Contracts
*   **Purpose**: Define data schemas exchanged between layers.
*   **Responsibilities**: Establish standard formats for layer boundaries, requests, and repository interfaces.
*   **Allowed Contents**: Boundary Models (request/response models), repository contracts, and shared interfaces.
*   **What it owns**: Contract interfaces, data DTO structures.
*   **What it must not own**: Business rules, domain validation, and query execution.

### 4. Spatial Lookup
*   **Purpose**: Resolve geographical coordinates to spatial index keys.
*   **Responsibilities**: Translate geographic coordinates to raster cell offsets and extract mapping unit values from the index grid.
*   **Dependencies**: Configuration, Shared Utilities.
*   **What it owns**: Grid coordinate calculations and binary stream offset parsing.
*   **What it must not own**: Attribute databases, classification dictionaries, and domain objects.

### 5. Soil Domain
*   **Purpose**: Define core soil science models and validation rules.
*   **Responsibilities**: Structure entities (`SoilObservation`, `SoilProfile`, `SoilLayer`, `SoilProperty`, `SoilClassification`) and enforce domain validation.
*   **Dependencies**: None (should remain independent of all other modules).
*   **What it owns**: Domain entity structures, validation logic, and profile sorting rules.
*   **What it must not own**: Spatial lookup math, database engines, and serialization codecs.

### 6. Data Access (Repository)
*   **Purpose**: Implement database query adapters and map persistence rows to domain models.
*   **Responsibilities**: Query attribute databases, pull vertical soil layers, and resolve integer codes using dictionary lookups.
*   **Dependencies**: Soil Domain, Configuration, Shared Utilities, Contracts.
*   **What it owns**: Database connections, repository implementations, and persistence adapters.
*   **What it must not own**: Spatial coordinates, endpoint definitions, and ingestion scripting.

### 7. Dataset Processing
*   **Purpose**: Ingest and preprocess raw soil datasets offline.
*   **Responsibilities**: Parse raw GIS datasets, build optimized spatial indexes, validate outputs using dedicated dataset adapters, and staging files.
*   **Dependencies**: Configuration, Shared Utilities.
*   **What it owns**: Dataset adapters (e.g. HWSD, SoilGrids adapters), migration scripts, and database creation pipelines.
*   **What it must not own**: Runtime coordinate lookups and API response formatting.

### 8. Configuration
*   **Purpose**: Manage global settings, environmental parameters, and path variables.
*   **Responsibilities**: Load environment settings, provide system path configurations, and export database credentials.
*   **Dependencies**: None.
*   **What it owns**: Config maps, file paths, and environment variable loaders.
*   **What it must not own**: Runtime data and domain business rules.

### 9. Shared Utilities
*   **Purpose**: Provide common helper functions across the backend.
*   **Responsibilities**: Provide mathematical utilities, coordinate parsers, logging wrappers, constants, and exceptions.
*   **Dependencies**: None.
*   **What it owns**: Logging decorators, string formatters, constants, exceptions, and geographic math utilities.
*   **What it must not own**: Core database schemas, domain entities, and request handlers.

---

## Dependency Rules

To prevent coupling and maintain structural maintainability, the following dependency constraints are strictly enforced:

```text
  Interfaces
      ↓ (depends on)
  Application Services, Contracts, Configuration, Shared Utilities
  
  Application Services
      ↓ (depends on)
  Spatial Lookup, Data Access, Soil Domain, Configuration, Shared Utilities, Contracts
  
  Data Access
      ↓ (depends on)
  Soil Domain, Configuration, Shared Utilities, Contracts
  
  Spatial Lookup / Dataset Processing
      ↓ (depends on)
  Configuration, Shared Utilities
```

*   **Soil Domain** has **no dependencies** on other modules.
*   **Spatial Lookup** can only depend on **Configuration** and **Shared Utilities**.
*   **Data Access** depends on **Soil Domain**, **Configuration**, **Shared Utilities**, and **Contracts**.
*   **Dataset Processing** depends on **Configuration** and **Shared Utilities**.
*   **Application Services** depends on **Spatial Lookup**, **Soil Domain**, **Data Access**, **Configuration**, **Shared Utilities**, and **Contracts**.
*   **Shared Utilities** and **Configuration** have **no dependencies** on other logical modules.

---

## Data Flow Through the Backend

The execution data flow for resolving coordinate lookups follows these steps:

1.  **Request Entry**: The `Interfaces` module receives a coordinate query.
2.  **Input Validation**: `Interfaces` converts parameters into a Coordinate request model.
3.  **Spatial Resolution**: `Application Services` invokes the `Spatial Lookup` module, which parses the spatial grid index and extracts the location index key.
4.  **Attribute Querying**: `Application Services` passes the Key to the `Data Access` module.
5.  **Data Retrieval**: `Data Access` queries the database, resolves property codes against dictionary lookup tables, and maps raw rows into `SoilDomain` structures (e.g., layers, profiles).
6.  **Observation Compilation**: `Application Services` aggregates the returned domain entities and compiles them into a unified `SoilObservation` domain object.
7.  **Response Construction**: `Interfaces` receives the `SoilObservation` from the application layer, serializes it, and returns the final response.

---

## Extension Strategy
*   **Adding a New Soil Dataset**:
    Create a new dataset adapter class in `Dataset Processing` to normalize the new dataset's attributes. In `Data Access`, write a dataset-specific repository implementation that satisfies the standard repository contract. The new repository returns standardized `SoilObservation` and `SoilProfile` domain objects, ensuring the rest of the application remains unchanged.
*   **Adding a New Service**:
    Define the service request/response models in `Contracts` and `Soil Domain`. Write the query operations in `Data Access`. Create the request controllers in `Application Services`. The new service is added without modifying the boundaries of the spatial lookup engine or preprocessing pipeline.

---

## Risks
*   **Leaky Domain Boundaries**: Database concepts leaking into the `Soil Domain` layer, causing domain entities to mirror specific table schemas.
*   **Performance Gaps**: Inefficient seeking inside the raw spatial binary grid leading to slow lookup times.
*   **Circular Dependencies**: Importing orchestrator services inside domain models, which will break the dependency tree.
*   **Coupling to Testing**: Hardcoding test data configurations inside production modules rather than loading them dynamically in the test runners.
