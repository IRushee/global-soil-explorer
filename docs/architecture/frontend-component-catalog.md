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

---

## 4. Responsive Layout Manager

To support various user environments (field researchers on tablets, office scientists on dual 4K monitors, and field workers on mobile phones), the UI implements a dynamic **Layout Manager**:

### A. Responsive Breakpoint Layout Rules
*   **Desktop & Large Monitors**:
    *   *SidebarPanel*: Fixed width (360px), docked left.
    *   *ScientificInfoPanel*: Resizable split pane docked bottom (occupying 40% height) or docked right (occupying 30% width).
    *   *Floating Panels*: User can pop out secondary tools (e.g. dynamic chart comparison, query logs) into floating, draggable windows.
*   **Tablets (Landscape/Portrait)**:
    *   *SidebarPanel*: Collapsible drawer overlays map. Swiping from the left edge pulls it out.
    *   *ScientificInfoPanel*: Sliding bottom drawer. Capped at 50% height with touch handle.
*   **Mobile Devices**:
    *   *Single-Panel focus mode*: Map fills screen by default. Selecting a coordinate opens the `ScientificInfoPanel` as a full-screen modal overlays, with tab-bar switching at the bottom. Sidebar controls open via hamburger buttons.

---

## 5. Scientific Display Profiles

To prevent cluttering the interface with irrelevant columns, users select a **Display Profile** that shapes the content displayed in the panels. Rather than custom CSS overrides, this is driven by Zustand store visibility filter arrays:

| Display Profile | Primary Focused Sections | Hidden/Collapsed Sections | Target User Audience |
| :--- | :--- | :--- | :--- |
| **`Simple`** | Classification, Top-layer Texture, Water Regime description | Deep chemical properties, Hydraulic properties | General public, education |
| **`Research`** | Full Taxonomy, C:N Ratios, CEC Soil/Clay, Environmental Context | None (All fields expanded) | Soil scientists, climatologists |
| **`Agriculture`** | Root depths obstacles, Land Limitations, pH, Nitrogen, Organic Carbon | Bulk densities, SOTER classifications | Agronomists, farmers, planners |
| **`Engineering`** | Bulk Density, Coarse Fragments, Impermeable Layer, Soil Texture | Organic carbon, WRB phases, C:N ratio | Civil engineers, site planners |
| **`Developer`** | All attributes + raw `codes` blocks, latency metrics, SMU metadata | None | API integrators, system testers |

