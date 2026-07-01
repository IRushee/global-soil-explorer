# Global Soil Explorer: System Blueprint

This document serves as the definitive reference blueprint for the entire Global Soil Explorer platform. It consolidates the backend architecture, frontend architecture, pipelines, and caching layers into a single cohesive system layout.

---

## 1. High-Level System Architecture

This diagram illustrates the separation of concerns across the network boundary. It details client-side state, the extensible **Plugin Registry**, the authentication boundary, background workers, and backend observability.

```mermaid
graph TD
    %% Browser Boundary
    subgraph Browser ["Web Browser Client Layer"]
        subgraph Auth ["Authentication & Security Boundary"]
            Anon["Anonymous Access"]
            Res["Researcher Profile"]
            Admin["Administrator Console"]
            Mgr["Dataset Manager"]
            Dev["Plugin Developer Tools"]
        end

        subgraph FE ["React Application Framework"]
            UI["UI Components (Radix UI + Tailwind)"]
            EB["Application Event Bus (Typed Events)"]
            CM["Command Engine (State Transactions)"]
            ST["Zustand Store (UI & Client State)"]
        end

        subgraph PR ["Plugin Registry System"]
            DP["Dataset Plugins"]
            RP["Renderer Plugins"]
            EP["Export Plugins"]
            SP["Search Plugins"]
            AP["Analysis Plugins"]
            OP["Overlay Plugins"]
        end

        ME["Map Engine Wrapper (MapLibre/Cesium/Leaflet)"]
    end

    %% Network Boundary
    Anon --> UI
    Res --> UI
    Admin --> UI
    Mgr --> UI
    Dev --> UI
    UI --> CM
    CM --> EB
    EB --> PR
    PR --> ME
    ST --> UI

    Browser -- "HTTP requests / WebSockets" --> Edge

    %% CDN and Edge Routing
    subgraph Edge ["Edge Infrastructure (Optional for Scale)"]
        CDN["CDN Cache (Cloudflare / CloudFront)"]
        TS["Tile Service (Direct Vector/Raster tiles)"]
    end
    CDN --> TS

    %% Backend Boundary
    subgraph Backend ["FastAPI Application Server"]
        subgraph API ["API & Processing Boundary"]
            REST["REST API Endpoint Router"]
            BG["Background Worker Engine (Optional)"]
            EQ["Export Jobs Queue (Optional)"]
            TG["On-The-Fly Tile Generator (Optional)"]
        end

        subgraph Obs ["Observability Engine (Optional)"]
            Log["Logging (Loguru/JSON)"]
            Met["Metrics (Prometheus/StatsD)"]
            Trc["Tracing (OpenTelemetry)"]
            HC["Health Checks (/v1/health)"]
            Err["Error Reporting (Sentry)"]
        end

        subgraph APP ["Backend Services"]
            AS["Application Service"]
            SL["Spatial Lookup Service"]
            REP["SQLite Repository"]
            DA["Scientific Dataset Adapter (SoilGrids/SSURGO Translation)"]
        end
        
        subgraph DOM ["Domain Model Layer"]
            COORD["Coordinate Validation"]
            OBS["SoilObservation (Aggregate Root)"]
            PROF["SoilProfile"]
            LAY["SoilLayer"]
        end

        subgraph DATA ["Persistence Datasets"]
            BIL["HWSD2.bil (Binary grid raster)"]
            HDR["HWSD2.hdr (Georeference metadata)"]
            SQL["SQLite Database (hwsd.db)"]
            LKP["Code Lookups (D_* tables)"]
        end
    end

    Edge -- "REST Queries" --> REST
    Edge -- "Direct Tile Requests" --> TS
    TS -- "Raw Tiles Generation" --> TG

    REST --> AS
    REST --> Obs
    BG --> EQ
    AS --> SL
    AS --> REP
    SL --> BIL
    SL --> HDR
    REP --> DA
    DA --> DOM
    REP --> SQL
    REP --> LKP
    REP --> Obs
```

---

## 2. End-to-End Query Sequence Diagram

This sequence diagram traces the complete lifecycle of a map interaction click resolving to a scientific observation query.

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant UI as UI View (Map Canvas)
    participant Cmd as SelectCoordinateCommand
    participant Bus as AppEventBus
    participant QP as Coordinate Pipeline
    participant Cache as React Query Cache
    participant CDN as CDN Edge Cache (Optional)
    participant API as FastAPI Backend (/v1/soil)
    participant AS as Application Service
    participant SL as Spatial Lookup (Raster)
    participant Repo as SQLite Repository
    participant DA as Scientific Dataset Adapter
    participant Dom as Domain Models (SoilObservation)

    User->>UI: Clicks coordinate on Map
    UI->>Cmd: Execute (lat, lon)
    Cmd->>Bus: Dispatch 'CoordinateSelected'
    Bus->>QP: Trigger Fetch pipeline
    QP->>Cache: Query cache for (lat, lon)
    
    alt Cache Hit
        Cache-->>QP: Return cached SoilObservation JSON
    else Cache Miss
        QP->>CDN: GET /v1/soil?latitude=Y&longitude=X
        alt CDN Cache Hit
            CDN-->>QP: Return cached observation
        else CDN Cache Miss
            CDN->>API: Route query to API
            API->>AS: get_soil_observation(Coordinate)
            AS->>SL: resolve(Coordinate) -> Key (smu_id)
            SL-->>AS: Key resolved (e.g. 10221)
            AS->>Repo: get_by_key(smu_id)
            Repo->>Repo: Query SQLite HWSD2_LAYERS & HWSD2_SMU
            Repo->>DA: Send raw data tuples
            DA->>DA: Translate dataset naming/schema formats (HWSD -> Domain)
            DA->>Dom: Construct SoilObservation aggregate
            Dom-->>DA: Return assembled Domain
            DA-->>Repo: Return Domain SoilObservation
            Repo-->>AS: Return SoilObservation
            AS-->>API: Return SoilObservation
            API->>API: Pydantic Serializer maps to Response Schema
            API-->>CDN: Return JSON Response Payload
            CDN-->>QP: Return JSON Response Payload
            QP->>Cache: Store in cache
        end
    end

    QP->>QP: Frontend Adapter maps JSON to standard client type
    QP->>UI: Update state & scientific panel displays profile layers
    UI-->>User: Visualizes vertical horizon charts & parameters table
```

---

## 3. Physical Deployment Topology & Infrastructure Options

To allow the platform to run easily on a single developer laptop (Local Stack) while maintaining architectural guidelines for high-load production scaling (Scale Stack), infrastructure components are divided into Required and Optional roles.

### A. Minimal Stack (Required for local development and run-from-laptop)
For default HWSD queries, static assets and coordinates querying route directly through the FastAPI backend to read SQLite and raster assets locally. No external caches or queues are required:

```
[ Browser / Client ] ──(REST Queries)──► [ FastAPI App (Uvicorn) ] ──► [ SQLite DB / Raster Files ]
```

### B. Scale Stack (Optional layers for high-load production environments)
For large-scale vector tile serving and asynchronous analysis, static and vector tiles bypass the main FastAPI application server, routing directly to the dedicated Tile Service.

```mermaid
graph TD
    subgraph Client ["Client Devices"]
        Browser["Web Browser Client"]
    end

    subgraph CDNLayer ["Distribution Layer (Optional)"]
        CDN["Edge CDN (Cloudflare / CloudFront)"]
    end

    subgraph Core ["Minimal Stack (Required)"]
        FastAPI["FastAPI App (REST API / Uvicorn)"]
        DB["SQLite DB (hwsd.db)"]
        Raster["Binary Raster (HWSD2.bil/.hdr)"]
    end

    subgraph ScaleServices ["Scale Stack (Optional)"]
        TS["Tile Service (Static/Vector Tile Host)"]
        Worker["Background Worker (Celery/RQ)"]
        Redis["Redis (Jobs Queue & Rate Limiter)"]
    end

    Browser -- "HTTPS" --> CDN
    CDN -- "Vector / Static Tiles" --> TS
    CDN -- "REST Queries (/v1/*)" --> FastAPI
    FastAPI <--> Redis
    Worker <--> Redis
    FastAPI <--> DB
    FastAPI <--> Raster
    Worker --> DB
    TS --> Raster
```

### C. Infrastructure Dependency Classification

*   **Required Infrastructure**:
    *   **FastAPI**: Server framework hosting the scientific API endpoints.
    *   **SQLite**: Databases layer housing attribute lookups and mapping layers data.
    *   **Raster Files (`.bil` / `.hdr`)**: Georeferenced cell rasters holding spatial indices.
*   **Optional Infrastructure (Production Scaling)**:
    *   **CDN (Content Delivery Network)**: Caches static tile files and REST queries close to users.
    *   **Tile Service (Tile Server)**: Serves map tile protocols (e.g., MVT vector tiles) directly without routing through the REST API.
    *   **Redis**: Key-value data cache and background task broker.
    *   **Celery / RQ**: Asynchronous background workers managing long-running jobs (e.g. dynamic reports generation, bulk spatial clips).
    *   **Sentry / Prometheus**: Server observability, logging, and error tracking metrics.

---

## 4. Cache Hierarchy & Invalidation Policies

The platform maintains a highly efficient 9-tier cache hierarchy to minimize latency:

| Level | Tier | Target Latency | Technology | Invalidation Policy |
| :--- | :--- | :--- | :--- | :--- |
| **L1** | **React State** | < 1ms | Zustand | Reset on coordinate/dataset switch |
| **L2** | **TanStack Query** | < 1ms | In-Memory Cache | Stale-time: 5 minutes; manual refetch triggers |
| **L3** | **Service Worker** | 2 - 10ms | Cache Storage API | Least Recently Used (LRU) - Max 100MB limit |
| **L4** | **Browser HTTP Cache** | 2 - 10ms | Browser Disk | Controlled by Cache-Control headers |
| **L5** | **CDN Cache (Optional)** | 15 - 50ms | Edge Server | Purge on new dataset release deployment |
| **L6** | **FastAPI Cache (Optional)** | 5 - 15ms | In-Memory (Redis) | Time-to-Live (TTL): 24 hours |
| **L7** | **SQLite Page Cache** | < 1ms | RAM | Managed by SQLite Engine (PRAGMA cache_size) |
| **L8** | **OS Page Cache** | < 1ms | RAM | Managed by Linux/macOS kernel page buffers |
| **L9** | **Physical Disk** | 1 - 5ms | SSD | Persistence layer - never invalidated |

---

## 5. Segmented Query Pipelines

To scale the query processing paths independently, queries are split into four dedicated pipelines:

### A. Viewport Pipeline (Map tiles)
`User Pan/Zoom` → `Viewport Box Bounding` → `Service Worker Cache` → `CDN Tile Service` → `Map WebGL Rendering`

### B. Coordinate Pipeline (Scientific details)
`Map Click` → `Coord Validation` → `TanStack Cache` → `REST API` → `Scientific Dataset Adapter` → `Zustand Store` → `Panel Display`

### C. Search Pipeline (Geocoding)
`Search Bar Text` → `Debounce` → `Geocoder Provider` → `Location Autocomplete` → `Coordinate selected event`

### D. Analysis Pipeline (Spatial analytics)
`Polygon selection` → `Validation` → `Background Queue Worker` → `GeoJSON Export / Statistics Table`

---

## 6. Interface Versioning Matrix

To maintain backward compatibility as the system evolves, every layer interface is explicitly versioned:

*   **REST API**: Versioned via URL path prefixes (e.g., `/v1/soil`). Legacy routes are retained as aliases.
*   **Event Contracts**: Event payload schemas are versioned via the event envelope (e.g., `{ type: 'CoordinateSelected', version: '1.0', payload: { lat, lon } }`).
*   **Plugin API**: The plugin registries validate provider interfaces on registration. Interface upgrades increment the plugin minor version.
*   **Scientific Dataset Adapter Interface**: Backend adapters inherit versioned abstract base classes (e.g., `BaseDatasetAdapterV1`).
*   **Export Schema**: Standardized export JSON schemas contain a metadata version string (`schema_version: "1.0"`).
*   **Tile Schema**: MVT vector tile schemas define key names and properties inside standard versioned tile specifications (e.g., `v1/tile/{z}/{x}/{y}.mvt`).

---

## 7. System Lifecycles Diagrams

These diagrams provide a detailed visual overview of operational lifecycles within the Global Soil Explorer.

### A. Application Startup & Plugin Discovery
```mermaid
graph TD
    Start["1. System Process Initiated"]
    Env["2. Load Environment Config"]
    DBInit["3. Open SQLite Connection Pools"]
    LocLkp["4. Load Lookups to Memory (D_* tables)"]
    PlgDisc["5. Scan /plugins/ directory"]
    RegPlg["6. Register & Validate Providers"]
    WarmCache["7. Trigger Cache Pre-warming"]
    Ready["8. Server Ready (Accept Requests)"]

    Start --> Env
    Env --> DBInit
    DBInit --> LocLkp
    LocLkp --> PlgDisc
    PlgDisc --> RegPlg
    RegPlg --> WarmCache
    WarmCache --> Ready
```

### B. Graceful Shutdown Sequence
```mermaid
graph TD
    Term["1. SIGTERM / SIGINT Received"]
    Refuse["2. Stop Accepting New Requests"]
    BgWrk["3. Wait for Active Background Jobs to Finish"]
    FlushLog["4. Flush Logs to Disk"]
    ClosePool["5. Close SQLite Connection Pools"]
    CloseRedis["6. Disconnect Queue & Cache Pools"]
    Exit["7. Process Terminated Successfully"]

    Term --> Refuse
    Refuse --> BgWrk
    BgWrk --> FlushLog
    FlushLog --> ClosePool
    ClosePool --> CloseRedis
    CloseRedis --> Exit
```

---

## 8. First-Class Study Area Abstractions

To ensure study areas are driven completely by configuration data rather than hardcoded client logic, we establish a standardized metadata schema representing an active **StudyArea** entity.

### A. StudyArea Data Schema
```typescript
interface StudyArea {
  id: string;                         // Unique study area identifier (e.g., "europe_central")
  name: string;                       // Localized descriptive name (e.g., "Central Europe Grid")
  projection: string;                 // EPSG code or proj4 coordinate system definition
  bounds: [[number, number], [number, number]]; // Bounding box limits (SW, NE lat/lon coordinates)
  availableDatasets: string[];        // Active datasets registered in this area (e.g., ["hwsd_v2"])
  defaultZoom: number;                // Starting map zoom level (e.g., 6.0)
  maxZoom: number;                    // Maximum allowed map detail level
  availableBasemaps: string[];        // List of basemap IDs registered
  tileEndpoint: string;               // URL pattern of the vector/raster tile service
  apiEndpoint: string;                // Base URL pattern for observations queries
  plugins: string[];                  // Analysis/Search plugin IDs enabled for this study area
  capabilities: DatasetCapabilities;  // Consolidated active capabilities constraints
}
```

By registering different `StudyArea` records (e.g. `India`, `Australia`, `Custom Grid`), the entire client map bounds, geocoders, and available data tabs adapt automatically.

---

## 9. Map Render Layer Stack

To prevent z-ordering layout collisions (where overlay polygons cover label text, or query selections slide underneath the terrain layer), Map Engine implementations must strictly adhere to the following layer render order stack:

```
┌────────────────────────────────────────────────────────┐
│ UI Overlays (Scale bars, Crosshairs, Legends)         │ ◄ Top Layer (Interactive overlay)
├────────────────────────────────────────────────────────┤
│ Labels & Typography (Place names, Road shields)        │
├────────────────────────────────────────────────────────┤
│ Query Markers & Pins (Search results, Click location)  │
├────────────────────────────────────────────────────────┤
│ Active Measurements (Drawn ruler distances, shapes)    │
├────────────────────────────────────────────────────────┤
│ Selection Outlines (Highlighted active soil SMU)      │
├────────────────────────────────────────────────────────┤
│ Scientific Overlays (MVT Polygons / Raster soils)      │
├────────────────────────────────────────────────────────┤
│ Topographic Terrain Relief (Hillshading, Contours)     │
├────────────────────────────────────────────────────────┤
│ Administrative Boundaries (Country / State borders)    │
├────────────────────────────────────────────────────────┤
│ Base Map Vector (Land mass, Water bodies fill)         │ ◄ Bottom Layer (Background)
└────────────────────────────────────────────────────────┘
```

---

## 10. Information Panel Architecture

Because this platform centers primarily around **Scientific Observations**, the `ScientificInfoPanel` has a specialized, componentized layout hierarchy mapping to the scientific aggregate outputs:

```
┌────────────────────────────────────────────────────────┐
│                   Information Panel                    │
├────────────────────────────────────────────────────────┤
│  Summary Section (Coord, Weather, Koppen Climate)      │
├────────────────────────────────────────────────────────┤
│  Profile Tabs selector (Dominant share percentage)     │
├────────────────────────────────────────────────────────┤
│  Layout Grid:                                          │
│  ┌─────────────────────────┬────────────────────────┐  │
│  │  Vertical Horizon Chart │ Measurements Tables    │  │
│  │  (Depth vs Properties)  │ ├── Physical properties│  │
│  │                         │ ├── Chemical parameters│  │
│  │                         │ └── Hydraulic stats    │  │
│  └─────────────────────────┴────────────────────────┘  │
├────────────────────────────────────────────────────────┤
│  Context Card:                                         │
│  ├── Hydrologic context descriptions                   │
│  └── Land limitations growth modifiers                 │
├────────────────────────────────────────────────────────┤
│  Metadata & Provenance attribution card                │
├────────────────────────────────────────────────────────┤
│  Related Datasets recommendation links                 │
├────────────────────────────────────────────────────────┤
│  Export Toolbox (JSON, CSV, PDF, Share link triggers)  │
└────────────────────────────────────────────────────────┘
```

---

## 11. Consolidated Search Providers Interface

All search types implement a unified search handler interface, enabling polymorphic geocoding and attribute lookup:

```typescript
interface SearchResultItem {
  id: string;
  label: string;
  category: 'coordinate' | 'location' | 'scientific_attribute' | 'dataset' | 'bookmark' | 'history';
  coordinate: { lat: number; lon: number };
  score: number;
  metadata?: Record<string, any>;
}

interface SearchProvider {
  id: string;
  name: string;
  search(query: string, bounds?: [[number, number], [number, number]]): Promise<SearchResultItem[]>;
}
```

The Search Module coordinates registry lookups across standard search adapter implementations:
*   `CoordinateSearchProvider`: Parses decimal/DMS notation coordinates.
*   `LocationSearchProvider`: Queries external Nominatim/Mapbox geocoders.
*   `ScientificAttributeSearchProvider`: Scans taxonomies (e.g. "Luvisols").
*   `DatasetSearchProvider`: Searches available layers (e.g. "clay").
*   `BookmarkSearchProvider`: Checks user's annotated bookmarks list.
*   `HistorySearchProvider`: Searches local history logs store.

---

## 12. Internationalization (i18n) Strategy

To support multi-language localizations in the field while maintaining scientific and scientific-database reproducibility:
1.  **Stable Scientific Names**: Scientific constants (e.g. taxonomy designations like `Luvisols`, soil codes like `LVcr`, standard measurement keys like `organic_carbon`) remain **strictly untranslated** in database cells and API JSON files.
2.  **UI Label Localization**: User-facing labels, field descriptors, and menus are localized using an i18n framework (e.g. `react-i18next`). UI keys map to translatable translation files:
    *   `measurements.chemical.ph_water` → `"pH (Water)"` (EN) / `"pH (Eau)"` (FR)
    *   `limitations.root_depth_description` → `"Root depth accessibility"` (EN) / `"Accessibilité de la profondeur des racines"` (FR)

---

## 13. Styling Theme Abstractions

To simplify dark mode, accessibility high-contrast rules, and map readability overlays, styling tokens are structured into four segregated theme abstraction layers:

```
┌────────────────────────────────────────────────────────┐
│                   Theme Configuration                  │
├────────────────────────────────────────────────────────┤
│  Application Theme (Tailwind HSL colors, dark mode)    │
├────────────────────────────────────────────────────────┤
│  Map Theme (MapLibre vector styling rules, roads fill) │
├────────────────────────────────────────────────────────┤
│  Scientific Theme (Soil colors, texture colors)        │
├────────────────────────────────────────────────────────┤
│  Accessibility Theme (Colorblind options, large text) │
└────────────────────────────────────────────────────────┘
```

---

## 14. Offline Fieldwork Capabilities

To support field surveys where network coverage is absent, the system defines four operational offline stages:

```
[ Stage 1: Online ] (Full connection; network fetches and real-time CDN tile downloads)
        │
        ▼
[ Stage 2: Offline Available ] (Service Worker cache pre-warmed for designated study areas)
        │
        ▼
[ Stage 3: Offline Read Only ] (REST requests resolved from LocalStorage; cached map tiles rendered)
        │
        ▼
[ Stage 4: Offline Analysis ] (Local Turf.js spatial clip operations; geojson file export)
```

---

## 15. Role-Based Authorization Model

Security configurations enforce a strict client-side role hierarchy to govern access to workspace editing tools and database management screens:

| Access Role | Privileges | Target UI Access Controls |
| :--- | :--- | :--- |
| **`Anonymous`** | Read-only coordinate queries, view overlays | View map, read info panel details |
| **`Researcher`**| Anonymous + Save Projects, bookmark coordinate queries | Unlock Saved Projects tabs, write annotations |
| **`Dataset Manager`** | Researcher + Upload datasets, update metadata lookups | Access data manager control panel screens |
| **`Plugin Developer`**| Researcher + Register custom providers, inspect metrics | Access developer plugin register tab, inspect logs |
| **`Administrator`** | All permissions (Full system override access) | Unlock full application config console panel |
