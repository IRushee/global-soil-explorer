# Map Architecture: WebGIS Foundation

This document defines the architectural wrapper around MapLibre GL JS. It establishes baseline abstractions for maps, layers, styling, and study area constraints.

---

## 1. Map Abstractions

To isolate MapLibre GL JS from the features layer, all WebGIS interactions pass through a clean wrapper interface.

### A. Basemap Registry
The map wrapper maintains a registry of basemap styles:
*   `light-vector`: Clean, typography-focused vector basemap for high-contrast data display.
*   `dark-vector`: Dark, minimal contrast basemap optimized for colorful raster layers.
*   `satellite-hybrid`: Orthophoto tile basemap overlayed with boundary vector lines.
*   `terrain-hillshade`: Topographic contours with hillshade relief.

### B. Overlay Layer Registry
Overlays represent spatial scientific datasets overlayed on top of the basemap. The `LayerRegistry` defines:
```typescript
interface OverlayLayer {
  id: string;
  title: string;
  description: string;
  dataset: string;
  renderer: string;
  type: 'raster' | 'vector' | 'geojson';
  sourceUrl: string;
  visible: boolean;
  opacity: number;
  minZoom: number;
  maxZoom: number;
  queryable: boolean;
  downloadable: boolean;
  exportable: boolean;
  cachePolicy: {
    maxAgeSeconds: number;
    persist: boolean;
  };
  refreshPolicy: 'on_mount' | 'manual' | 'never';
  dependencies: string[]; // List of other layer IDs that must be loaded first
  legend: LegendConfig;
}
```

---

## 2. Layers & Styling Pipeline

```
Layer State (Zustand Store) 
       │
       ▼
Map Wrapper layer sync loop (React useEffect)
       │
       ├── Check source exist (add if missing)
       ├── Check layer exist (add if missing)
       ├── Apply Visibility: setLayoutProperty(layerId, 'visibility', 'visible' | 'none')
       ├── Apply Opacity: setPaintProperty(layerId, 'raster-opacity' | 'fill-opacity', opacityValue)
       └── Apply Layer Order: moveLayer(layerId, beforeId)
```

### Dynamic Styling
For vector layers, dynamic styling allows recoloring elements (e.g., color-coding classification polygons or soil pH values) on the client side using MapLibre paint expressions:
```json
["interpolate", ["linear"], ["get", "ph"], 
  4.0, "#d73027", 
  7.0, "#fee08b", 
  10.0, "#1a9850"
]
```

### Legend Support
Each `OverlayLayer` exposes a `legend` config that the UI layer decodes to render standard visual legends (discrete color blocks, gradient sliders, or classification textures).

---

## 3. Study Area Abstractions

To prevent map queries outside target zones, the engine enforces a `StudyAreaConstraint` policy:
*   **Bounding Box Bounds**: Restricts camera panning and zoom limits using `map.setMaxBounds(bounds)`.
*   **Visual Polygon Masking**: Adds a boundary layer masking non-study areas with a dark or semi-transparent fill.
*   **Coordinate Bounds Check**: Restricts spatial REST queries. Clicking outside the study area limits does not trigger API requests, preventing unnecessary infrastructure load.

---

## 4. Renderer Abstraction

To support multiple map visualization backends without rewriting core features (like search, panel display, or data download), the frontend defines a **Unified Renderer Interface**:

```
 ┌─────────────────────────────────────────────────────────────┐
 │                       Feature Modules                       │
 │  (Search, Spatial Filters, Information Panel, Export Tools)  │
 └──────────────────────────────┬──────────────────────────────┘
                                │ Calls
                                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │                  Unified Renderer Interface                 │
 │ (initialize, setCenter, setZoom, addLayer, removeLayer, ...)│
 └──────────────────────────────┬──────────────────────────────┘
                                │ Adapts
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
 ┌──────────────┐        ┌──────────────┐        ┌──────────────┐
 │  MapLibre    │        │    Cesium    │        │   Leaflet    │
 │  Adapter     │        │    Adapter   │        │   Adapter    │
 └──────────────┘        └──────────────┘        └──────────────┘
```

The feature modules interact strictly with the generic `MapRenderer` type definition:
```typescript
interface MapRenderer {
  initialize(containerId: string, options: MapOptions): void;
  setCenter(lat: number, lon: number): void;
  setZoom(zoom: number): void;
  addLayer(layer: OverlayLayer): void;
  updateLayer(layerId: string, updates: Partial<OverlayLayer>): void;
  removeLayer(layerId: string): void;
  on(event: 'click' | 'zoomend' | 'moveend', handler: (e: any) => void): void;
  destroy(): void;
}
```

This guarantees the platform can support 3D globes (Cesium) or simple 2D maps (Leaflet) by exchanging the active adapter without changing any React layout code.

---

## 5. Dataset Capability Matrix

The UI must adapt dynamically depending on the scientific capabilities of the underlying active dataset. Rather than hardcoding dataset-specific UI switches, we enforce a **Capability-Driven UI model**:

### A. Capability Types Definition
```typescript
interface DatasetCapabilities {
  supportsDynamicDepthQueries: boolean;   // Can query soil at any arbitrary depth level?
  supportsMultipleProfiles: boolean;       // Does a pixel resolve to multiple composite profiles?
  supportsHydrologicMetrics: boolean;      // Exposes drainage class, regime, and layers?
  supportsGrowthLimitations: boolean;      // Exposes root depth obstacles and phases?
  maxVerticalDepthCm: number;              // Max depth interval supported (e.g. 200cm)
  supportedExportFormats: ('json' | 'csv' | 'geojson' | 'pdf' | 'png')[];
}
```

### B. Matrix Registration
```typescript
const DATASET_CAPABILITY_MATRIX: Record<string, DatasetCapabilities> = {
  hwsd_v2: {
    supportsDynamicDepthQueries: false,    // Fixed layer intervals (0-30cm, 30-100cm, etc.)
    supportsMultipleProfiles: true,        // Resolves up to 9 composite profiles per SMU
    supportsHydrologicMetrics: true,
    supportsGrowthLimitations: true,
    maxVerticalDepthCm: 200,
    supportedExportFormats: ['json', 'csv', 'pdf', 'png'],
  },
  soilgrids: {
    supportsDynamicDepthQueries: true,     // Supports depth interpolation
    supportsMultipleProfiles: false,       // Renders single point estimates
    supportsHydrologicMetrics: false,
    supportsGrowthLimitations: false,
    maxVerticalDepthCm: 200,
    supportedExportFormats: ['json', 'csv', 'geojson', 'pdf'],
  },
  ssurgo: {
    supportsDynamicDepthQueries: false,
    supportsMultipleProfiles: true,
    supportsHydrologicMetrics: true,
    supportsGrowthLimitations: true,
    maxVerticalDepthCm: 150,
    supportedExportFormats: ['json', 'csv', 'geojson', 'pdf', 'png'],
  }
};
```

*   **UI Adherence**: If `supportsMultipleProfiles` is `false`, the profile selector tabs are hidden. If `supportsDynamicDepthQueries` is `true`, depth sliders are unlocked for continuous vertical seeking.

