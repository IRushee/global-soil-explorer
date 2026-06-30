# Backend Project Structure: Global Soil Explorer

---

## Purpose
This document defines the logical project structure, module responsibilities, and dependency rules of the Global Soil Explorer backend service. It translates the high-level system architecture into a clear software organizational design, ensuring developers and AI assistants implement code in consistent, decoupled modules.

---

## Design Principles
1.  **Strict Dependency Direction**: Dependencies must flow inwards. Higher-level orchestration services depend on contracts and domain models, but the core domain models must have zero external dependencies.
2.  **Strict Separation of Concerns**: Each module has a specific, non-overlapping responsibility (e.g., separating offline preprocessing pipelines from runtime querying).
3.  **De-coupled Data Access**: Database logic is isolated from domain and application services, preventing storage schemas from leaking into business logic.
4.  **Fail-Safe Processing**: Error checking occurs at boundary interfaces, preventing corrupted states from entering core processing stages.

---

## Module Responsibilities

### 1. Interfaces
*   **Purpose**: Provide entry points into the application (API controllers, web controllers, CLI runners).
*   **Responsibilities**: Translate external client requests into application service commands and present results (e.g., JSON response serialization).
*   **Dependencies**: Application, Contracts, Domain, Configuration, Shared Utilities.
*   **What it owns**: Routing configurations, API controllers, request/response DTO handlers.
*   **What it must not own**: Core business logic workflows, database access, and spatial seeking.

### 2. Application Services (Orchestration)
*   **Purpose**: Coordinate workflows and request flows.
*   **Responsibilities**: Coordinate lookup and query processing sequences, invoking repository queries and compiling observations.
*   **Dependencies**: Contracts, Domain, Configuration, Shared Utilities.
*   **What it owns**: Orchestration services, workflow coordinators.
*   **What it must not own**: Database connections, direct spatial seeking, and web routing.

### 3. Contracts
*   **Purpose**: Define the interfaces and data schemas exchanged between layers.
*   **Responsibilities**: Establish standard abstract repository interfaces, lookup service interfaces, and request/response models.
*   **Dependencies**: Domain.
*   **What it owns**: Repository interfaces (`SoilObservationRepository`), lookup service interfaces (`SpatialLookupService`), and contract abstractions.
*   **What it must not own**: Scientific domain validation rules, active query execution, and ingestion pipelines.

### 4. Infrastructure (Data Access & Spatial Lookup)
*   **Purpose**: Implement the interfaces defined in Contracts using specific technologies.
*   **Responsibilities**: Implement database adapters, coordinate spatial lookups, parse files, and manage connection pools.
*   **Dependencies**: Contracts, Domain, Configuration, Shared Utilities.
*   **What it owns**: Concrete database repositories, concrete lookup service implementations, database connection handlers, and file readers.
*   **What it must not own**: API endpoint routing and core business workflows.

### 5. Soil Domain
*   **Purpose**: Define core scientific soil entities and validation rules.
*   **Responsibilities**: Structure entities (`SoilObservation`, `SoilProfile`, `SoilLayer`, `SoilProperty`, `SoilClassification`) and enforce domain validation.
*   **Dependencies**: None (remains completely independent of all other modules).
*   **What it owns**: Domain entity structures, validation logic, and profile stacking/sorting rules.
*   **What it must not own**: Spatial lookup logic, database engines, and serialization codecs.

### 6. Dataset Processing
*   **Purpose**: Ingest and preprocess raw soil datasets offline.
*   **Responsibilities**: Parse raw GIS datasets, build optimized spatial indexes, convert raw databases into query-optimized formats, validate outputs, and stage runtime files.
*   **Dependencies**: Configuration, Shared Utilities.
*   **What it owns**: Extraction scripts, transformation rules, indexing tools, and database creation pipelines.
*   **What it must not own**: Runtime queries, client state, and API routing.

### 7. Configuration
*   **Purpose**: Manage global settings, environmental parameters, and path variables.
*   **Dependencies**: None.
*   **What it owns**: Config maps, file paths, and environment variable loaders.

### 8. Shared Utilities
*   **Purpose**: Provide common helper functions across the backend (logging, exception definitions, math helpers).
*   **Dependencies**: None.

---

## Dependency Rules

To prevent coupling and maintain structural maintainability, the Domain remains the central independent layer, and all dependencies flow strictly inwards:

```text
  Interfaces
      ↓
  Application
      ↓
  Contracts
      ↓
  Infrastructure
```

*   **Domain**: The central independent layer with **zero external dependencies** on other modules or layers.
*   **Contracts** depends strictly on **Domain**.
*   **Infrastructure** implements the abstract classes in Contracts and depends on **Contracts** and **Domain** (as well as Configuration and Shared Utilities).
*   **Application** depends on **Contracts** and **Domain** (as well as Configuration and Shared Utilities).
*   **Interfaces** depends on **Application** (and Configuration and Shared Utilities).
*   **Dataset Processing** depends on **Configuration** and **Shared Utilities**.
*   **Shared Utilities** and **Configuration** have **no dependencies** on other logical modules.

---

## Data Flow Through the Backend

The execution data flow for resolving coordinate lookups follows these steps:

1.  **Request Entry**: The `Interfaces` module receives a coordinate query.
2.  **Input Validation**: `Interfaces` converts parameters into a Coordinate request model.
3.  **Request Orchestration**: `Application Services` receives the request.
4.  **Spatial Resolution**: `Application Services` invokes the concrete `SpatialLookupService` (from Infrastructure, via Contracts interface) to resolve coordinates to a spatial identifier.
5.  **Data Retrieval**: `Application Services` queries the concrete `SoilObservationRepository` (from Infrastructure, via Contracts interface) using the spatial identifier.
6.  **Database Mapping**: The repository queries the database, resolves property codes against dictionary lookup tables, and maps raw storage records into `SoilDomain` structures (properties, layers, classifications, profiles).
7.  **Observation Compilation**: The repository compiles these entities into a unified `SoilObservation` domain object and returns it.
8.  **Response Construction**: `Interfaces` receives the `SoilObservation`, serializes it, and returns the final response.
