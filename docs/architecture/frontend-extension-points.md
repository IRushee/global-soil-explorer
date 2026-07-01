# Frontend Extension Points

This document outlines the architectural extension points designed to make the WebGIS platform completely dataset-agnostic, extensible for spatial analysis, and compatible with future user collaboration workspaces.

---

## 1. Multi-Dataset Adaptability

The API integration layer separates the REST payload ingestion from the presentation components using a **Unified Domain Translator Pattern**:

```
                       API Response (JSON)
          ┌─────────────────────┼─────────────────────┐
          ▼                     ▼                     ▼
      [HWSD v2]            [SoilGrids]            [SSURGO]
          │                     │                     │
          ▼                     ▼                     ▼
   Translator (v1)      Translator (SoilGrids)  Translator (SSURGO)
          │                     │                     │
          └─────────────────────┼─────────────────────┘
                                ▼
                   Standardized UI Observation Schema
                                │
                                ▼
                       Presentation Components
```

*   **Dataset Independence**: Adding a new global dataset (e.g. SoilGrids) only requires writing a new Scientific Dataset Translator class implementing the front-end `ObservationSchema` interface. The UI components (e.g. `LayerDepthChart`, `MeasurementsTable`) read this standard schema and do not need to change.

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

---

## 4. Plugin Registries Architecture

To ensure the core application code remains locked and never requires modification when adding new features, the frontend leverages a central **Plugin Registry System**. Developers register custom providers that conform to strict interface contracts:

```typescript
class ExtensionRegistry<K, P> {
  private providers: Map<K, P> = new Map();

  register(key: K, provider: P): void {
    if (this.providers.has(key)) {
      throw new Error(`Provider already registered: ${String(key)}`);
    }
    this.providers.set(key, provider);
  }

  get(key: K): P {
    const provider = this.providers.get(key);
    if (!provider) {
      throw new Error(`Provider not found: ${String(key)}`);
    }
    return provider;
  }

  list(): K[] {
    return Array.from(this.providers.keys());
  }
}
```

### A. Registry Categories

1.  **`DatasetProviders`**: Handles data decoding and capabilities mapping (e.g. `HWSDv2Provider`, `SoilGridsProvider`).
2.  **`BasemapProviders`**: Sets basemap URL strings, metadata attributions, and dynamic style templates (e.g. `MapboxVectorProvider`, `OpenStreetMapRasterProvider`).
3.  **`OverlayProviders`**: Manages styling rules, layer order index rules, and legend templates for overlays.
4.  **`RendererProviders`**: Adapts the map engine viewport to different rendering technologies (e.g. `MapLibreRenderer`, `Cesium3DRenderer`, `Leaflet2DRenderer`).
5.  **`SearchProviders`**: Registers geocoding lookup pipelines (e.g. `NominatimSearchProvider`, `MapboxGeocodeProvider`, `ScientificCoordinateSearchProvider`).
6.  **`ExportProviders`**: Serializes soil observations and map viewports into target formats.
7.  **`AnalysisProviders`**: Registers spatial computation tools (e.g. `BufferAnalysisProvider`, `ZonalStatsAnalysisProvider`).

---

## 5. Export Architecture

Exporting scientific observations is handled via the registered `ExportProviders`. Each provider implements a standard serialization interface:

```typescript
interface ExportProvider {
  format: 'json' | 'csv' | 'geojson' | 'pdf' | 'png' | 'clipboard' | 'share';
  export(observation: SoilObservation, metadata: MapViewportState): Promise<ExportResult>;
}
```

### B. Standard Export Providers Mappings

*   **`JSONExportProvider`**: Serializes the `SoilObservation` object directly to a formatted `.json` file.
*   **`CSVExportProvider`**: Flattens layer depth intervals and physical/chemical measurement parameters into comma-separated tabular rows (one row per layer depth).
*   **`GeoJSONExportProvider`**: Wraps the active coordinate and attributes in a standard `FeatureCollection` schema for loading directly into desktop GIS tools (QGIS, ArcGIS).
*   **`PDFExportProvider`**: Generates a clean, print-optimized scientific report containing tables and vertical horizon depth charts.
*   **`PNGExportProvider`**: Generates a high-resolution snapshot of the active Map Viewport complete with legends and scale bars.
*   **`ClipboardExportProvider`**: Formats the selected soil classifications and coordinates as a clean Markdown snippet.
*   **`ShareLinkExportProvider`**: Compiles the query parameters into a compressed URL hash for sharing active workspaces.

