# Frontend Extension Points

This document outlines the architectural extension points designed to make the WebGIS platform completely dataset-agnostic, extensible for spatial analysis, and compatible with future user collaboration workspaces.

---

## 1. Multi-Dataset Adaptability

The API integration layer separates the REST payload ingestion from the presentation components using a **Unified Domain Adapter Pattern**:

```
                       API Response (JSON)
          ┌─────────────────────┼─────────────────────┐
          ▼                     ▼                     ▼
      [HWSD v2]            [SoilGrids]            [SSURGO]
          │                     │                     │
          ▼                     ▼                     ▼
   Adapter (v1)          Adapter (SoilGrids)     Adapter (SSURGO)
          │                     │                     │
          └─────────────────────┼─────────────────────┘
                                ▼
                   Standardized UI Observation Schema
                                │
                                ▼
                       Presentation Components
```

*   **Dataset Independence**: Adding a new global dataset (e.g. SoilGrids) only requires writing a new Adapter class implementing the front-end `ObservationSchema` interface. The UI components (e.g. `LayerDepthChart`, `MeasurementsTable`) read this standard schema and do not need to change.

---

## 2. Spatial Analysis Tool Extensions

To support client-side spatial calculations (e.g. intersection, area buffers, slope calculation) in the future:
*   **Geospatial Processing Engine (Turf.js Integration)**: The Map Engine includes hooks to mount client-side analysis pipelines.
*   **Draw Control Integration**: MapLibre wrapper defines mounting points for `MapboxDraw` or `MapLibreDraw` controls to allow users to draw custom polygons for clipping grid cells.

---

## 3. Workspace, Bookmarks, and Projects

The frontend architecture includes a **Workspace Persistence Layer**:
1.  **State Serializers**: A standard interface is established to serialize the active workspace state (active coordinate pin, layer opacities, zoom bounding box, and custom annotations) into a JSON workspace file.
2.  **Storage Providers**: The persistence layer exposes adapters to save/load workspace profiles from:
    *   `LocalStorageProvider`: Storing workspaces on the client's local browser.
    *   `CloudApiProvider`: Syncing projects to a user account database via future REST endpoints.
    *   `FileExportProvider`: Downloading the workspace configurations as a local `.json` file for offline sharing.
