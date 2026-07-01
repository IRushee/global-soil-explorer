# Frontend Component Catalog

This document defines the layout specifications and modular presentation components for the Global Soil Explorer user interface. These components strictly separate rendering and styling from data validation and queries.

---

## 1. Primary Layout Hierarchy

```
┌────────────────────────────────────────────────────────────────────────┐
│                              HeaderBar                                 │
├────────────────────────────────┬───────────────────────────────────────┤
│                                │                                       │
│                                │                                       │
│                                │                Map View               │
│                                │           (MapLibre WebGL)            │
│         Sidebar Panel          │                                       │
│  (Search, Filters, Layers)     │                                       │
│                                ├───────────────────────────────────────┤
│                                │        Scientific Info Panel          │
│                                │    (Profiles, Layers, Soil Stats)     │
└────────────────────────────────┴───────────────────────────────────────┘
```

### A. Core Layout Containers
*   **`HeaderBar`**: Global branding, coordinate search input, settings toggle, and API health indicator.
*   **`SidebarPanel`**: Left-side drawer containing the Layer Manager, Spatial Filters, and Search inputs.
*   **`MapView`**: Full-screen canvas mounting MapLibre GL.
*   **`ScientificInfoPanel`**: Bottom/Right responsive drawer dedicated to displaying detailed soil profiles and measurements for the queried pixel.

---

## 2. Shared Presentation Components

### A. CoordinateInput
*   *Purpose*: Captures manual latitude/longitude values.
*   *Validation*: Enforces numeric formats, latitude bounds (`[-90, 90]`), and longitude bounds (`[-180, 180]`). Supports decimal degrees and Degrees-Minutes-Seconds (DMS) parsing.

### B. FilterAccordion
*   *Purpose*: Collapsible sidebar filters grouping spatial, taxonomic, and physical-chemical ranges.
*   *Controls*: Comboboxes for taxonomy classes; range sliders for pH, sand%, and organic carbon ranges.

### C. ProfileTabSelector
*   *Purpose*: Switch between multiple component profiles belonging to the queried spatial Mapping Unit.
*   *Display*: Lists composition share percentage (e.g. "Profile 1 - Luvisols (65%)", "Profile 2 - Regosols (35%)") to inform the user of soil heterogeneity.

### D. LayerDepthChart (VerticalHorizonChart)
*   *Purpose*: Renders chemical and physical measurement metrics vertically by depth.
*   *Visuals*: Y-Axis represents soil depth in centimeters (pointing downwards, e.g. 0 to -150cm); X-Axis displays values (e.g., pH, clay share %). Shows color-coded horizontal blocks representing layer intervals.

### E. MeasurementsTable
*   *Purpose*: Dense tabular display of structured layer measurements grouped by category (physical, chemical, hydraulic).
*   *Interactive features*: Expand/collapse rows, unit toggles (e.g., pH, percent, g/kg), and copy-to-clipboard options.

---

## 3. Thematic Display Constraint

By default, the WebGIS client does **NOT** display thematic property maps (such as a global raster colored by pH ranges).
*   The primary product of this platform is the **Spatial Soil Observation** (raw point query resolving profile verticality).
*   The basemap overlays display the active soil classification units (MVT polygons or raster masks).
*   Properties are inspected interactively in the `ScientificInfoPanel` to prevent scientific interpolation misrepresentations.
