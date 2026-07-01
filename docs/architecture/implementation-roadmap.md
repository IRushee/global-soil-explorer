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

### 1. Environment (milestone-01-development-environment)
*   **Objective**: Configure the developer workspace, code styling formats, package manager boundaries, and test structure.
*   **Deliverables**: Project configuration profiles, package dependency files, linter/formatter rules, and initial test directories.
*   **Success Criteria**: Running the validation suite passes successfully with zero formatting, type-checking, or linting errors.

### 2. Backend Skeleton (milestone-02-backend-skeleton)
*   **Objective**: Establish the basic backend package structure and project directory boundaries.
*   **Deliverables**: Directory scaffolding, basic application setup, and initial modular structure.
*   **Success Criteria**: Clean package imports with no circular dependencies in basic scaffolding.

### 3. Domain Architecture (milestone-03-domain-architecture)
*   **Objective**: Define the conceptual system architecture, module structure, and dependency boundaries before implementing functionality.
*   **Deliverables**: Architecture blueprint documents, design guidelines, and folder structure scaffolding.
*   **Success Criteria**: Architectural specifications are accepted and frozen.

### 4. Coordinate (milestone-04-coordinate)
*   **Objective**: Implement the `Coordinate` value object representing geographic locations with validation rules.
*   **Deliverables**: `Coordinate` domain model implementation and associated unit tests.
*   **Success Criteria**: Geographic coordinate checks ensure latitude and longitude boundaries are validated.

### 5. Soil Property (milestone-05-soil-property)
*   **Objective**: Implement the `SoilProperty` value object containing soil chemical and physical measurements.
*   **Deliverables**: `SoilProperty` domain model and unit tests.
*   **Success Criteria**: Validates value ranges and units for individual properties.

### 6. Soil Classification (milestone-06-soil-classification)
*   **Objective**: Implement the `SoilClassification` domain model representing taxonomy mapping (FAO/WRB).
*   **Deliverables**: `SoilClassification` domain model and lookup tables support.
*   **Success Criteria**: Standard WRB and FAO soil classification attributes are correctly encapsulated.

### 7. Soil Layer (milestone-07-soil-layer)
*   **Objective**: Implement the `SoilLayer` value object representing vertical depth slices of soil profiles.
*   **Deliverables**: `SoilLayer` domain model and unit tests.
*   **Success Criteria**: Enforces depth ordering and layers stacking constraints.

### 8. Soil Profile (milestone-08-soil-profile)
*   **Objective**: Implement the `SoilProfile` aggregate representing vertical stacked sequences of layers at a location.
*   **Deliverables**: `SoilProfile` domain model and integration tests.
*   **Success Criteria**: Layers are validated for depth coherence and sequence sorting.

### 9. Soil Observation (milestone-09-soil-observation)
*   **Objective**: Implement the aggregate root `SoilObservation` uniting coordinates, profiles, and metadata.
*   **Deliverables**: `SoilObservation` domain model and tests.
*   **Success Criteria**: Combines spatial coordinates with structural soil profiles and metadata.

### 10. Domain Contracts (milestone-10-domain-contracts)
*   **Objective**: Define standard abstract interfaces for database repositories and coordinate lookup services.
*   **Deliverables**: Repository and lookup interface definitions (`SoilObservationRepository`, `SpatialLookupService`) under `contracts`.
*   **Success Criteria**: Contracts are fully decoupled from storage/raster implementations and type check cleanly.

### 11. Preprocessing Pipeline (milestone-11-preprocessing-pipeline)
*   **Objective**: Build the framework for the offline processing pipeline, establishing logging context and configurations.
*   **Deliverables**: Ingestion orchestrator code, configuration files, and preprocessing context helpers.
*   **Success Criteria**: Pipeline scaffolding runs with configurable environment paths.

### 12. MDB Reader (milestone-12-mdb-reader)
*   **Objective**: Build the offline utility to read raw tabular data from Access `.mdb` databases.
*   **Deliverables**: Tabular reader modules using `mdbtools`.
*   **Success Criteria**: MDB files are parsed with correct schema/type casting.

### 13. Database Generation (milestone-13-database-generation)
*   **Objective**: Run database conversion and sentinel cleaning.
*   **Deliverables**: DB generation scripts mapping raw inputs to SQLite and clearing negative flag values.
*   **Success Criteria**: Normalized `hwsd.db` SQLite database is generated with zero corruption.

### 14. SQLite Repository (milestone-14-sqlite-repository)
*   **Objective**: Develop SQLite repository query handlers and domain mapper logic.
*   **Deliverables**: Database connection handlers, query builders, and database row-to-domain mapping helpers.
*   **Success Criteria**: Queries retrieve correct soil profiles and classification dictionaries mapped to validated domain objects.

### 15. Spatial Lookup (milestone-15-spatial-lookup)
*   **Objective**: Implement grid coordinate translations and spatial lookup handlers using direct raster seeks.
*   **Deliverables**: Coordinate translators and spatial grid lookup handlers (`BILRasterSpatialLookupService`).
*   **Success Criteria**: Coordinate queries successfully resolve spatial positions to retrieve valid spatial identifiers.

### 16. Application Service (milestone-16-application-service)
*   **Objective**: Implement orchestration services to tie the query pipeline together.
*   **Deliverables**: Orchestrator service invoking lookup, fetching database attributes, and compiling domain objects.
*   **Success Criteria**: Integration tests verify end-to-end lookup flow from coordinates to domain models.

### 17. FastAPI (milestone-17-fastapi)
*   **Objective**: Create the web API controllers and request routing protocols.
*   **Deliverables**: FastAPI endpoint routes and request routing controllers.
*   **Success Criteria**: REST endpoints serve coordinates queries.

### 18. Domain & Repository Freeze (milestone-18-domain-and-repository-freeze)
*   **Objective**: Perform quality audits on backend domain validation and repository performance.
*   **Deliverables**: Repository audit reports, domain coverage validations, and baseline performance benchmarks.
*   **Success Criteria**: Domain and persistence layers are declared frozen.

### 19. Application Freeze (milestone-19-application-freeze)
*   **Objective**: Verify application service orchestration, concurrency capabilities, and edge cases.
*   **Deliverables**: Application freeze report and concurrent stress test results.
*   **Success Criteria**: No memory leaks or exception leakage under concurrent load.

### 20. API Contract (milestone-20-api-contract)
*   **Objective**: Ensure that API responses strictly conform to documentation schemas and performance criteria.
*   **Deliverables**: OpenAPI schema definition, API contract verification reports, and response structure freezing.
*   **Success Criteria**: API responses match schemas and run under 20ms latency.

### 21. Frontend Architecture (milestone-21-frontend-architecture)
*   **Objective**: Establish frontend workspace structure, directory layout, and library dependencies.
*   **Deliverables**: React/TypeScript scaffolding, routing mapping, and Zustand stores setup.
*   **Success Criteria**: Scaffold compiles successfully with zero lint/formatting issues.

### 22. Frontend Foundation (milestone-22-frontend-foundation)
*   **Objective**: Implement the map wrapper component, query pipeline state management, and core presentation modules.
*   **Deliverables**: Map wrapper with MapLibre GL JS and component rendering frames.
*   **Success Criteria**: Map is responsive and coordinates selection correctly updates global state.

### 23. UX Freeze (milestone-23-ux-freeze)
*   **Objective**: Freeze user interface design templates, keyboard shortcuts, styling components, and accessibility support.
*   **Deliverables**: Completed UX design specs, accessibility checklists, and dashboard elements.
*   **Success Criteria**: Interactive visual dashboard elements are stable, accessible, and ready for integration.

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
