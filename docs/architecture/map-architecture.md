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
  name: string;
  type: 'raster' | 'vector' | 'geojson';
  sourceUrl: string;
  visible: boolean;
  opacity: number;
  minZoom: number;
  maxZoom: number;
  legendConfig: LegendConfig;
  styleRules: StyleRule[];
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
Each `OverlayLayer` exposes a `legendConfig` that the UI layer decodes to render standard visual legends (discrete color blocks, gradient sliders, or classification textures).

---

## 3. Study Area Abstractions

To prevent map queries outside target zones, the engine enforces a `StudyAreaConstraint` policy:
*   **Bounding Box Bounds**: Restricts camera panning and zoom limits using `map.setMaxBounds(bounds)`.
*   **Visual Polygon Masking**: Adds a boundary layer masking non-study areas with a dark or semi-transparent fill.
*   **Coordinate Bounds Check**: Restricts spatial REST queries. Clicking outside the study area limits does not trigger API requests, preventing unnecessary infrastructure load.
