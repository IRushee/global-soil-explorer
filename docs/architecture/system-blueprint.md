# Global Soil Explorer: System Blueprint

This document serves as the definitive reference blueprint for the entire Global Soil Explorer platform. It consolidates the backend architecture, frontend architecture, pipelines, and caching layers into a single cohesive system layout.

---

## 1. High-Level System Architecture

This diagram illustrates the separation of concerns across the network boundary. It details client-side state, the extensible **Plugin Registry**, the authentication boundary, background workers, and backend observability.

```mermaid
graph TD
    %% Browser Boundary
    subgraph Browser ["Web Browser Client Layer"]
        subgraph Auth ["Authentication Boundary"]
            Anon["Anonymous User Access"]
            AuthUser["Authenticated User Access"]
            Work["User Workspace Manager"]
            Proj["Saved Projects / Bookmarks"]
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
    AuthUser --> Work
    Work --> Proj
    UI --> CM
    CM --> EB
    EB --> PR
    PR --> ME
    ST --> UI

    Browser -- "HTTP requests / WebSockets" --> Edge

    %% CDN and Edge Routing
    subgraph Edge ["Edge Infrastructure"]
        CDN["CDN Cache (Cloudflare / CloudFront)"]
        TS["Tile Service (Direct Vector/Raster tiles)"]
    end
    CDN --> TS

    %% Backend Boundary
    subgraph Backend ["FastAPI Application Server"]
        subgraph API ["API & Processing Boundary"]
            REST["REST API Endpoint Router"]
            BG["Background Worker Engine"]
            EQ["Export Jobs Queue"]
            TG["On-The-Fly Tile Generator"]
        end

        subgraph Obs ["Observability Engine"]
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
            DA["Dataset Adapter (SoilGrids/SSURGO Translation)"]
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
    participant CDN as CDN Edge Cache
    participant API as FastAPI Backend (/v1/soil)
    participant AS as Application Service
    participant SL as Spatial Lookup (Raster)
    participant Repo as SQLite Repository
    participant DA as Dataset Adapter
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
            DA->>DA: Translate dataset naming/schema formats
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

## 3. Physical Deployment Topology

To ensure high scalability and fast response times, static and vector tiles bypass the main FastAPI application server, routing directly to the dedicated Tile Service.

```mermaid
graph TD
    Browser["Web Browser Client"]
    CDN["Edge CDN (Cloudflare / CloudFront)"]
    TS["Tile Service (Static/Vector Tile Host)"]
    FastAPI["FastAPI App (REST API / Uvicorn)"]
    Worker["Background Worker (Celery/RQ)"]
    Redis["Redis (Jobs Queue & Rate Limiter)"]
    DB["SQLite DB (hwsd.db)"]
    Raster["Binary Raster (HWSD2.bil/.hdr)"]

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

---

## 4. Cache Hierarchy & Invalidation Policies

The platform maintains a highly efficient 9-tier cache hierarchy to minimize latency:

| Level | Tier | Target Latency | Technology | Invalidation Policy |
| :--- | :--- | :--- | :--- | :--- |
| **L1** | **React State** | < 1ms | Zustand | Reset on coordinate/dataset switch |
| **L2** | **TanStack Query** | < 1ms | In-Memory Cache | Stale-time: 5 minutes; manual refetch triggers |
| **L3** | **Service Worker** | 2 - 10ms | Cache Storage API | Least Recently Used (LRU) - Max 100MB limit |
| **L4** | **Browser HTTP Cache** | 2 - 10ms | Browser Disk | Controlled by Cache-Control headers |
| **L5** | **CDN Cache** | 15 - 50ms | Edge Server | Purge on new dataset release deployment |
| **L6** | **FastAPI Cache** | 5 - 15ms | In-Memory (Redis) | Time-to-Live (TTL): 24 hours |
| **L7** | **SQLite Page Cache** | < 1ms | RAM | Managed by SQLite Engine (PRAGMA cache_size) |
| **L8** | **OS Page Cache** | < 1ms | RAM | Managed by Linux/macOS kernel page buffers |
| **L9** | **Physical Disk** | 1 - 5ms | SSD | Persistence layer - never invalidated |

---

## 5. Segmented Query Pipelines

To scale the query processing paths independently, queries are split into four dedicated pipelines:

### A. Viewport Pipeline (Map tiles)
`User Pan/Zoom` → `Viewport Box Bounding` → `Service Worker Cache` → `CDN Tile Service` → `Map WebGL Rendering`

### B. Coordinate Pipeline (Scientific details)
`Map Click` → `Coord Validation` → `TanStack Cache` → `REST API` → `Dataset Adapter` → `Zustand Store` → `Panel Display`

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
*   **Dataset Adapter Interface**: Backend adapters inherit versioned abstract base classes (e.g., `BaseDatasetAdapterV1`).
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
