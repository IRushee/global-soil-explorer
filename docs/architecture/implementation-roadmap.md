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

### 1. Development Environment
*   **Objective**: Configure the developer workspace, code styling formats, package manager boundaries, and test structure.
*   **Deliverables**: Project configuration profiles, package dependency files, linter/formatter rules, and initial test directories.
*   **Dependencies**: None.
*   **Success Criteria**: Running the validation suite passes successfully with zero formatting, type-checking, or linting errors.

### 2. Backend Skeleton
*   **Objective**: Establish the backend module structure and dependency boundaries before implementing functionality.
*   **Deliverables**:
    *   Module layout
    *   Interfaces
    *   Dependency wiring
    *   Placeholder implementations
    *   Build configuration
*   **Dependencies**: Development Environment.
*   **Success Criteria**: The backend builds successfully with placeholder implementations and respects the approved architecture.

### 3. Domain Layer
*   **Objective**: Write the core scientific entities representing soil properties and layers.
*   **Deliverables**: Conceptual domain classes for profiles, layers, components, and properties.
*   **Dependencies**: Development Environment.
*   **Success Criteria**: Automated domain tests verify that vertical layers stack correctly and coordinates range checks pass without exceptions.

### 4. Dataset Processing
*   **Objective**: Build the offline pipeline script to transform raw datasets into normalized tabular structures and optimized grid indexes.
*   **Deliverables**: Data extraction, transformation, normalization, and verification scripts.
*   **Dependencies**: Backend Skeleton, raw datasets in `data/raw/hwsd/`.
*   **Success Criteria**: Preprocessing script runs to completion, creating an optimized database and index repository, with row and cell counts matching raw dataset inventories exactly.

### 5. Spatial Lookup
*   **Objective**: Develop the coordinate-to-grid offset converter and pixel index lookup tool.
*   **Deliverables**: Coordinate coordinate translator and binary raster stream parser.
*   **Dependencies**: Dataset Processing.
*   **Success Criteria**: Querying set coordinate benchmarks returns the correct Mapping Unit Keys matching verified dataset indexes.

### 6. Repository Layer
*   **Objective**: Develop database query interfaces to pull attribute tables and resolve codes using dictionaries.
*   **Deliverables**: Database connection handlers, relational query structures, and mapping helpers.
*   **Dependencies**: Domain Layer, Dataset Processing.
*   **Success Criteria**: Querying using a valid Mapping Unit Key returns a populated, validated Soil Profile domain object containing fully resolved dictionary text labels.

### 7. Application Services
*   **Objective**: Develop the request controller services, API routing parameters, and response serialization rules.
*   **Deliverables**: Request orchestrator service, API routes, data serialization templates, and error mapping rules.
*   **Dependencies**: Spatial Lookup, Repository Layer.
*   **Success Criteria**: Mock coordinate queries yield serialized Soil Profile payloads under sub-second processing response times.

### 8. User Interface Integration
*   **Objective**: Connect the browser map and charting interface to the runtime query services.
*   **Deliverables**: Interactive map click trigger, vertical profile charts, and legend panel.
*   **Dependencies**: Application Services.
*   **Success Criteria**: Clicking the map successfully converts coordinates, queries the backend service, and renders a vertical soil profile chart and description legends without lag.

### 9. Testing & Validation
*   **Objective**: Implement full automated coverage for unit, integration, and UI actions.
*   **Deliverables**: Test suites, coordinate fixtures, database mock environments.
*   **Dependencies**: User Interface Integration.
*   **Success Criteria**: Test runners report 100% pass rates for critical coordinates queries, database lookups, and error cases.

### 10. Documentation
*   **Objective**: Finalize installation scripts, user manuals, and deployment manifests.
*   **Deliverables**: Setup, workflow, and deployment markdown files.
*   **Dependencies**: Testing & Validation.
*   **Success Criteria**: A new developer can set up the workspace, ingest the data, pass tests, and start the system using only the documentation.

### 11. First Public MVP
*   **Objective**: Deliver a usable, fully integrated client-server application where users can interactively explore global soil datasets.
*   **Deliverables**: Compiled client package, executable API services, and default local configuration profiles.
*   **Dependencies**: Documentation, Testing & Validation.
*   **Success Criteria**: The unified client-server application runs successfully locally, allowing users to query coordinates and instantly view visual soil profiles.

---

## Milestone Risks

1.  **Environment Setup**: Package conflicts between developer operating systems.
2.  **Backend Skeleton**: Incorrect initial module boundary definitions leading to circular references.
3.  **Domain Layer**: Leaky boundaries causing database schema definitions to influence core domain structures.
4.  **Dataset Processing**: Missing database extraction drivers for legacy database formats (`.mdb`) on Unix-based development platforms (macOS/Linux).
5.  **Spatial Lookup**: Slow binary seeking performance when querying raw spatial formats under concurrent user loads.
6.  **Repository Layer**: Missing keys or orphaned mapping units in the database causing query joins to fail.
7.  **Application Services**: Serialization performance overhead slowing down API response generation.
8.  **UI Integration**: Client-side coordinate mapping errors or map rendering lag at high zoom levels.
9.  **Testing**: Brittle visual tests that break on minor styling changes.
10. **Documentation**: Outdated setup guidelines due to undocumented environmental configurations.
11. **First Public MVP**: Local client-server connection conflicts or file permission blocks.

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
