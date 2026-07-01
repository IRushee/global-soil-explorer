# Global Soil Explorer: Architecture Index

Welcome to the architectural documentation for the Global Soil Explorer. This directory serves as the master blueprint and reference for all contributors. It defines the scientific domain models, API schemas, backend processing layers, frontend WebGIS modules, and system lifecycles.

---

## Architecture Navigation Index

### 1. Vision
*   **Overview**: Core mission, project philosophy, scope boundaries, and development principles.
*   **Documentation**:
    *   [Project Principles](file:///Users/rushee/Projects/global-soil-explorer/docs/architecture/project-principles.md) - Design patterns and engineering guidelines.

### 2. Domain
*   **Overview**: Pure scientific domain model definitions, value objects, aggregates, and data types.
*   **Documentation**:
    *   [Master Information Model](file:///Users/rushee/Projects/global-soil-explorer/docs/architecture/master-information-model.md) - Complete structural definitions of all entities.
    *   [Scientific Attribute Catalog](file:///Users/rushee/Projects/global-soil-explorer/docs/architecture/scientific-attribute-catalog.md) - Exact mapping of scientific attributes, units, and ranges.
    *   [HWSD Domain Mapping](file:///Users/rushee/Projects/global-soil-explorer/docs/architecture/hwsd-domain-mapping.md) - Bridge mapping between HWSD fields and standard domain profiles.
    *   [Information Ownership Matrix](file:///Users/rushee/Projects/global-soil-explorer/docs/architecture/information-ownership-matrix.md) - Ownership boundaries for scientific coordinates, climates, metadata, and layers.

### 3. Backend
*   **Overview**: Persistence layers, SQLite structures, and spatial lookup engines.
*   **Documentation**:
    *   [Backend Structure](file:///Users/rushee/Projects/global-soil-explorer/docs/architecture/backend-structure.md) - Repository interfaces, raster Seeking offset calculation, and FastAPI lifecycle controllers.
    *   [Study Area Abstraction](file:///Users/rushee/Projects/global-soil-explorer/docs/architecture/study-area-abstraction.md) - Bounding box boundaries and data verification.

### 4. API
*   **Overview**: Public JSON contracts, routing versioning strategies, and error formats.
*   **Documentation**:
    *   [API Specification](file:///Users/rushee/Projects/global-soil-explorer/docs/architecture/api-specification.md) - Frozen endpoint descriptions and parameters.
    *   [API Traceability Matrix](file:///Users/rushee/Projects/global-soil-explorer/docs/architecture/api-traceability-matrix.md) - Clear field-by-field scientific owner, source tables, lookup mapping tables, and target frontend components.
    *   [API Contract Verification](file:///Users/rushee/Projects/global-soil-explorer/docs/verification/api-contract-verification.md) - Performance metrics, payload benchmarks, and serialization latency audits.

### 5. Frontend
*   **Overview**: Client frameworks, query lifecycles, and component catalogs.
*   **Documentation**:
    *   [Frontend Architecture](file:///Users/rushee/Projects/global-soil-explorer/docs/architecture/frontend-architecture.md) - Technology evaluation, system folders, and the complete 6-stage Query Pipeline.
    *   [Navigation & Routing Specification](file:///Users/rushee/Projects/global-soil-explorer/docs/architecture/navigation-specification.md) - Deep-linking URL serialization schema, view states, and accessibility key shortcuts.
    *   [Frontend Performance Plan](file:///Users/rushee/Projects/global-soil-explorer/docs/architecture/frontend-performance-plan.md) - CPU optimizations, Zustand selectors, chunk lazy loading, and virtualization.

### 6. WebGIS
*   **Overview**: Map layers wrapper, basemaps, styling filters, and viewport seeking.
*   **Documentation**:
    *   [Map Architecture](file:///Users/rushee/Projects/global-soil-explorer/docs/architecture/map-architecture.md) - MapLibre wrapping, overlay registries, paint expressions, and dataset capability matrices.

### 7. Plugins & Extension Points
*   **Overview**: Extension boundaries, registries, and dynamic plugins.
*   **Documentation**:
    *   [Frontend Extension Points](file:///Users/rushee/Projects/global-soil-explorer/docs/architecture/frontend-extension-points.md) - Unified Domain Adapters, Workspace persistence, Turf.js spatial analysis tools, and the seven core Plugin Registries.

### 8. Caching
*   **Overview**: Multi-tier caching policies and Service Worker handlers.
*   **Documentation**:
    *   [Tile Loading & Caching Strategy](file:///Users/rushee/Projects/global-soil-explorer/docs/architecture/tile-loading-strategy.md) - Viewport loading, speculative pre-fetching, and Service Worker LRU cache details.

### 9. Deployment
*   **Overview**: Server infrastructure scaling, CDN edge routes, and background workers.
*   **Documentation**:
    *   [System Blueprint Deployment Section](file:///Users/rushee/Projects/global-soil-explorer/docs/architecture/system-blueprint.md#3-physical-deployment-topology) - Visual overview of network edges, tile servers, and backend worker queues.

### 10. Extension Points
*   **Overview**: Swappable plugin interfaces and customization bounds.
*   **Documentation**:
    *   [Frontend Extension Points](file:///Users/rushee/Projects/global-soil-explorer/docs/architecture/frontend-extension-points.md) - Domain Adapters, Workspace persistence, Turf analysis tools, and Plugin Registries.

### 11. ADRs
*   **Overview**: Architecture Decision Records detailing domains, database structures, type safety, and contracts isolation rules.
*   **Documentation**:
    *   [ADR-001: Domain Model Purity](file:///Users/rushee/Projects/global-soil-explorer/docs/architecture/adr/adr-001-domain-model-purity.md)
    *   [ADR-002: Spatial Lookup Architecture](file:///Users/rushee/Projects/global-soil-explorer/docs/architecture/adr/adr-002-spatial-lookup-architecture.md)
    *   [ADR-003: SQLite Database Schema](file:///Users/rushee/Projects/global-soil-explorer/docs/architecture/adr/adr-003-sqlite-database-schema.md)
    *   [ADR-004: Repository Aggregation Strategy](file:///Users/rushee/Projects/global-soil-explorer/docs/architecture/adr/adr-004-repository-aggregation-strategy.md)
    *   [ADR-005: Coordination of Lookup Service](file:///Users/rushee/Projects/global-soil-explorer/docs/architecture/adr/adr-005-coordination-of-lookup-service.md)
    *   [ADR-006: Strict Typing and Type Safety](file:///Users/rushee/Projects/global-soil-explorer/docs/architecture/adr/adr-006-strict-typing-and-type-safety.md)
    *   [ADR-007: FastAPI and Application Layer Isolation](file:///Users/rushee/Projects/global-soil-explorer/docs/architecture/adr/adr-007-fastapi-and-application-layer-isolation.md)
    *   [ADR-008: Backend Contracts are Dataset-Independent](file:///Users/rushee/Projects/global-soil-explorer/docs/architecture/adr/adr-008-backend-contracts-are-dataset-independent.md)
    *   [ADR-009: Response Models Never Expose Persistence Concepts](file:///Users/rushee/Projects/global-soil-explorer/docs/architecture/adr/adr-009-response-models-never-expose-persistence-concepts.md)

### 12. System Blueprint
*   **Overview**: Consolidating diagrams for physical deployment, sequential querying, caching boundaries, and app lifecycles.
*   **Documentation**:
    *   [System Blueprint](file:///Users/rushee/Projects/global-soil-explorer/docs/architecture/system-blueprint.md) - Master reference.

### 13. Verification Documents
*   **Overview**: Audits, verification reports, and baseline validation benchmarks.
*   **Documentation**:
    *   [API Contract Verification](file:///Users/rushee/Projects/global-soil-explorer/docs/verification/api-contract-verification.md) - Performance metrics, payload benchmarks, and serialization latency audits.

