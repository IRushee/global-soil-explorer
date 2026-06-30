# Implementation Roadmap: Global Soil Explorer

---

## Purpose
This document defines a phased implementation roadmap for the Global Soil Explorer. It outlines chronological development milestones, target deliverables, success criteria, implementation risks, and the Definition of Done required to build a stable, performant Minimum Viable Product (MVP) based on the approved architecture.

---

## Development Principles
1.  **Incremental Progress**: Build and commit code incrementally in small, reviewable, and reversible steps.
2.  **Docs First**: Write or update design records and technical documentation before writing non-trivial features.
3.  **Fail Fast, Test Early**: Write automated unit and integration tests alongside modules, validating execution at every stage.
4.  **No Speculative Code**: Implement only the requirements defined for the active milestone, avoiding early optimization or speculative features.
5.  **Data Isolation**: Protect raw datasets under `data/raw/hwsd/` as read-only. Preprocessing outputs must reside exclusively in output cache folders.

---

## Milestones

### 1. Environment
*   **Objective**: Configure the developer workspace, code styling formats, package manager boundaries, and test structure.
*   **Deliverables**: Project configuration profiles, package dependency files, linter/formatter rules, and initial test directories.
*   **Success Criteria**: Running the validation suite passes successfully with zero formatting, type-checking, or linting errors.

### 2. Architecture
*   **Objective**: Define the conceptual system architecture, module structure, and dependency boundaries before implementing functionality.
*   **Deliverables**: Architecture blueprint documents, design guidelines, and folder structure scaffolding.
*   **Success Criteria**: Architectural specifications are accepted and frozen.

### 3. Domain
*   **Objective**: Write the core scientific value objects representing soil properties, layers, classifications, profiles, and observations.
*   **Deliverables**: Fully validated domain objects (`Coordinate`, `SoilProperty`, `SoilClassification`, `SoilLayer`, `SoilProfile`, `SoilObservation`) with comprehensive test suites.
*   **Success Criteria**: Automated domain tests verify vertical stacking boundaries, ordering, and data type invariants with zero errors.

### 4. Contracts
*   **Objective**: Define standard abstract interfaces for database repositories and coordinate lookup services.
*   **Deliverables**: Repository and lookup interface definitions (`SoilObservationRepository`, `SpatialLookupService`) under `contracts`.
*   **Success Criteria**: Contracts are fully decoupled from storage/raster implementations and type check cleanly.

### 5. Processing
*   **Objective**: Build the offline pipeline script to transform raw datasets into normalized SQLite tables and extract binary raster streams.
*   **Deliverables**: Data extraction, database conversion, validation scripts, and grid extraction scripts.
*   **Success Criteria**: The offline preprocessing script runs to completion, generating correct query-ready relational databases and extracted raster grids.

### 6. Repository
*   **Objective**: Develop SQLite repository query handlers and domain mapper logic.
*   **Deliverables**: Database connection handlers, query builders, and database row-to-domain mapping helpers.
*   **Success Criteria**: Queries retrieve correct soil profiles and classification dictionaries mapped to validated domain objects.

### 7. Spatial Lookup
*   **Objective**: Implement grid coordinate translations and spatial lookup handlers.
*   **Deliverables**: Coordinate translators and spatial grid lookup handlers.
*   **Success Criteria**: Coordinate queries successfully resolve spatial positions to retrieve valid spatial identifiers.

### 8. Application
*   **Objective**: Implement orchestration services to tie the query pipeline together.
*   **Deliverables**: Orchestrator service invoking lookup, fetching database attributes, and compiling domain objects.
*   **Success Criteria**: Integration tests verify end-to-end lookup flow from coordinates to domain models.

### 9. Interfaces
*   **Objective**: Create the web API controllers, request routing protocols, and client map interface dashboards.
*   **Deliverables**: FastAPI endpoint routes, JSON serialization schemas, visual browser map clicks, and vertical profile charting widgets.
*   **Success Criteria**: UI clicking maps resolves coordinates and renders vertical soil profile charts in under a second.

---

## Definition of Done (MVP Completion Criteria)

The Minimum Viable Product (MVP) is considered complete and ready for public launch when:
1.  **Code Quality**: All backend and frontend code compiles successfully with zero linting, formatting, or static type-checking errors.
2.  **Test Coverage**: All unit, integration, and UI test suites run and report a 100% pass rate.
3.  **Data Integrity**: The ingestion pipeline processes raw spatial grids and relational tables into optimized storage without data loss, validated against row-count checks.
4.  **Performance**: Spatial coordinate lookups and profile retrieval resolve in the browser under 1 second.
5.  **Usability**: A user with no prior GIS training can navigate the map, click a point, and view an understandable vertical soil profile chart.
6.  **Documentation**: Setup, workflow, API, and deployment documentation is updated, verified, and checked into the repository.
7.  **Architecture Compliance**: Every implemented module conforms to the approved architectural documents, dependency rules, and domain model.
