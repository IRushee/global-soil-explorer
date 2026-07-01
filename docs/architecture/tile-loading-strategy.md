# Tile Loading & Caching Strategy

This document defines the strategy for loading, caching, and managing spatial raster/vector tiles to maintain 60 FPS viewport navigation and minimize network traffic.

---

## 1. Viewport & Pan-Aware Loading

To optimize bandwidth and map responsiveness, the client implements dynamic viewport tile loading:
1.  **Lazy Loading**: Only tiles intersecting the active viewport boundaries are requested.
2.  **Pan-Aware Pre-fetching**: Using map panning speed and vector trajectory vectors, the client speculatively pre-fetches tiles in the direction of the camera movement.
3.  **Request Cancellation**: When the user pans away rapidly, incomplete tile network requests outside the new viewport are immediately aborted using `AbortController` integrations.

---

## 2. Zoom & Content-Aware Loading

1.  **Zoom-Level Scaling**:
    *   *Low Zoom (Global/Continental)*: Requests generalized, downsampled regional tiles to avoid loading massive high-resolution files.
    *   *High Zoom (Local/Field)*: Loads full 250m-resolution datasets (e.g. HWSD v2.0 grid details).
2.  **Content-Aware Masking**: The map client maintains a low-resolution bounding box mask of active data pixels (land areas). Viewport regions covering open water or oceans do not trigger tile requests.

---

## 3. Caching & Eviction Policies

```
             Map Engine (MapLibre GL) Request
                           │
                           ▼
              Check Memory Cache (In-Memory MapLibre) ───[HIT]───► Render
                           │
                         [MISS]
                           ▼
            Check Service Worker Cache Storage API ──────[HIT]───► Render
                           │
                         [MISS]
                           ▼
                     Fetch Network ───► Store in Cache & Memory ───► Render
```

### A. Memory Cache (L1 Cache)
*   *Implementation*: MapLibre internal texture cache (GL texture buffers).
*   *Capacity*: Configured dynamically based on browser hardware parameters (usually capped at 200 textures).

### B. Persistent Cache (L2 Cache)
*   *Implementation*: **Service Worker** intercepting requests and caching responses in the browser's **Cache Storage API**.
*   *Keying*: Unique URL identifiers including layer ID, zoom level, X coordinate, and Y coordinate.
*   *Eviction Policy*: Least Recently Used (LRU) policy. When cache size exceeds 100MB, the Service Worker evicts old tile assets.

---

## 4. Vector Tile Evolution

The loading and caching layer is designed to support Mapbox Vector Tiles (MVT) natively:
*   **Protobuf Parsing**: WebGL-based vector loaders deserialize binary protocol buffers (PBF) on worker threads.
*   **Client-Side Intersection**: The cache strategy treats vector tiles as pure raw data buffers. The same Service Worker caching and eviction pipelines apply to both vector tiles (`.pbf`) and raster tiles (`.png`/`.webp`).
