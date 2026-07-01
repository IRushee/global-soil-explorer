# Global Soil Explorer: System Blueprint

This document serves as the definitive reference blueprint for the entire Global Soil Explorer platform. It consolidates the backend architecture, frontend architecture, pipelines, and caching layers into a single cohesive system layout.

---

## 1. High-Level System Architecture

This diagram illustrates the separation of concerns across the network boundary, isolating client-side state and map rendering from the server-side processing, lookup, and repository databases.

```mermaid
graph TD
    %% Browser Boundary
    subgraph Browser ["Web Browser Client Layer"]
        subgraph FE ["React Application Framework"]
            UI["UI Components (Radix UI + Tailwind)"]
            ME["Map Engine Wrapper (MapLibre GL JS)"]
            EB["Application Event Bus (Typed Events)"]
            CM["Command Engine (State Transactions)"]
            QP["Query Pipeline (Validation & Fetching)"]
            ST["Zustand Store (UI & Client State)"]
            AC["API Client (Axios client)"]
        end
    end

    %% Network Boundary
    Browser -- "HTTP Requests (/v1/soil, /v1/health)" --> Backend

    %% Backend Boundary
    subgraph Backend ["FastAPI Application Server"]
        subgraph APP ["Application Boundary"]
            API["API Endpoints & Routers (app.py)"]
            AS["Application Service (service.py)"]
            SL["Spatial Lookup Service (raster_lookup.py)"]
            REP["SQLite Repository (sqlite_repository.py)"]
        end
        
        subgraph DOM ["Domain Model Layers"]
            COORD["Coordinate (lat, lon Validation)"]
            OBS["SoilObservation (Aggregate Root)"]
            PROF["SoilProfile (Composition Share)"]
            LAY["SoilLayer (Vertical intervals)"]
        end

        subgraph DATA ["Persistence & Scientific Datasets"]
            BIL["HWSD2.bil (Binary grid raster)"]
            HDR["HWSD2.hdr (Georeference metadata)"]
            SQL["SQLite Database (hwsd.db)"]
            LKP["Code Lookups (D_* tables)"]
        end
    end

    %% UI and Component connections
    UI --> CM
    CM --> EB
    EB --> QP
    QP --> ST
    ST --> UI
    QP --> AC

    %% Backend connections
    API --> AS
    AS --> SL
    AS --> REP
    SL --> BIL
    SL --> HDR
    REP --> SQL
    REP --> LKP
    REP --> DOM
    SL --> DOM
```

---

## 2. End-to-End Sequence Diagram (Map Click query flow)

This sequence diagram traces a coordinate point query from the initial click down to the data retrieval, domain assembly, serialization, and frontend presentation layers.

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant UI as UI View (Map Canvas)
    participant Cmd as SelectCoordinateCommand
    participant Bus as AppEventBus
    participant QP as Query Pipeline
    participant Cache as React Query Cache
    participant API as FastAPI Backend (/v1/soil)
    participant AS as Application Service
    participant SL as Spatial Lookup (Raster)
    participant Repo as SQLite Repository
    participant Dom as Domain Models (SoilObservation)

    User->>UI: Clicks coordinate on Map
    UI->>Cmd: Execute (lat, lon)
    Cmd->>Bus: Dispatch 'CoordinateSelected'
    Bus->>QP: Trigger Fetch pipeline
    QP->>Cache: Query cache for (lat, lon)
    
    alt Cache Hit
        Cache-->>QP: Return cached SoilObservation JSON
    else Cache Miss
        QP->>API: HTTP GET /v1/soil?latitude=Y&longitude=X
        API->>AS: get_soil_observation(Coordinate)
        AS->>SL: resolve(Coordinate) -> Key (smu_id)
        SL-->>AS: Key resolved (e.g. 10221)
        AS->>Repo: get_by_key(smu_id)
        Repo->>Repo: Query SQLite HWSD2_LAYERS & HWSD2_SMU
        Repo->>Repo: Resolve raw codes against lookups (D_*)
        Repo->>Dom: Construct SoilObservation aggregate
        Dom-->>Repo: Domain assembled
        Repo-->>AS: Return SoilObservation
        AS-->>API: Return SoilObservation
        API->>API: Pydantic Serializer maps to Response Schema
        API-->>QP: JSON Response Payload
        QP->>Cache: Store in cache
    end

    QP->>QP: Frontend Adapter maps JSON to standard client type
    QP->>UI: Update state & scientific panel displays profile layers
    UI-->>User: Visualizes vertical horizon charts & parameters table
```

---

## 3. Physical Deployment Topology

This diagram maps the current physical deployment boundaries and details how the future Content Delivery Network (CDN) and tile services scale the delivery of raster grids.

```mermaid
graph LR
    subgraph Client ["Client Device"]
        B["Browser (Chrome, Safari, Firefox)"]
        TC["Local Service Worker Cache"]
    end

    subgraph Edge ["Distribution Layer (Future CDN)"]
        CDN["CDN Edge Cache (Cloudflare / CloudFront)"]
    end

    subgraph AppServer ["Server Infrastructure"]
        FastAPI["FastAPI Web App (Uvicorn)"]
        DB["SQLite DB (hwsd.db)"]
        Raster["Binary Raster (HWSD2.bil/.hdr)"]
    end

    B <--> TC
    B <--> CDN
    CDN <--> FastAPI
    FastAPI <--> DB
    FastAPI <--> Raster
```

---

## 4. Cache Hierarchy & Latency Boundaries

To achieve rapid page load and coordinate lookups, data caches are layered across the entire hardware and networking path:

```
┌────────────────────────────────────────────────────────────────────────┐
│ Client-Side Memory (React State / Zustand)   | Latency: < 1ms          │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Client-Side Cache (React Query In-Memory)    | Latency: < 1ms          │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Browser Cache (Service Worker Cache Storage) | Latency: 2 - 10ms       │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Edge Cache (CDN / HTTP Cache Headers)        | Latency: 15 - 50ms      │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Web App Server (FastAPI Endpoint)            | Latency: 5 - 15ms       │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│ OS Page Cache (SQLite / Raster binary reads)  | Latency: < 1ms (RAM)    │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Physical Disk Storage (SSD SQLite / Raster)  | Latency: 1 - 5ms (I/O)  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Complete Query Pipeline Lifecycle

This flowchart defines the end-to-end processing steps, transformations, and data models of a coordinate query lifecycle:

```
[ User Interaction ] ──► (Map canvas selection or search input)
        │
        ▼
[ Command Execution ] ──► (Create Command instance to track state change)
        │
        ▼
[ Event Dispatched ] ──► (Command dispatches Event to application bus)
        │
        ▼
[ Query Builder ] ──► (Query pipeline compiles latitude, longitude, and active filters)
        │
        ▼
[ Client Validation ] ──► (Coordinates range validated; bad values blocked)
        │
        ▼
[ Cache Resolution ] ──► (Checks React Query for matching coordinates cache)
        │
        ▼
[ REST HTTP Client ] ──► (Pushes request to API with AbortController)
        │
        ▼
[ FastAPI App Routing ] ──► (Receives request, validates types, injects services)
        │
        ▼
[ Application Service ] ──► (Orchestrates coordinate seeks across spatial lookup & repository)
        │
        ▼
[ Spatial Lookup ] ──► (Seeks binary bil raster index for coordinate offsets)
        │
        ▼
[ SQLite Repository ] ──► (Fetches layers, maps taxonomy codes, resolves descriptors)
        │
        ▼
[ Domain Construction ] ──► (Builds domain models enforcing invariants)
        │
        ▼
[ API Serializer ] ──► (Pydantic schema validation, filters codes, builds response JSON)
        │
        ▼
[ Frontend Adapter ] ──► (Transforms API JSON into stable unified interface)
        │
        ▼
[ Store Update ] ──► (Updates Zustand store variables, triggers component render)
        │
        ▼
[ Scientific Panel ] ──► (Vertical horizon charts and chemical tables render details)
```
