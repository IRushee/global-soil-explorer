# Frontend Architecture: Global Soil Explorer

This document defines the core frontend architecture for the Global Soil Explorer WebGIS application. It justifies the selected technology stack, defines the system directory structure, establishes clean boundaries, and ensures the client remains strictly dataset-independent and study-area-agnostic.

---

## 1. Technology Evaluation & Recommendations

We evaluated the primary options for building a modern, high-performance WebGIS client:

### A. Map Engine: MapLibre GL JS vs. Leaflet
*   **Leaflet**:
    *   *Pros*: Lightweight (38KB gzipped), highly mature, large plugin ecosystem, simple DOM-based rendering.
    *   *Cons*: Performance degrades quickly when rendering thousands of vectors; lacks native support for WebGL-based vector tiles, client-side dynamic styling, and smooth 3D terrain/globe projections.
*   **MapLibre GL JS**:
    *   *Pros*: WebGL/WebGPU accelerated rendering, native support for Mapbox Vector Tiles (MVT), smooth panning/zooming, client-side layer styling via the Mapbox Style Specification, and high-performance rendering of dense spatial datasets (such as soil grids).
    *   *Cons*: Slightly larger bundle size, steeper learning curve.
*   **Recommendation**: **MapLibre GL JS**. High-performance rendering of global scientific datasets requires WebGL/WebGPU acceleration and native vector tile styling.

### B. Core Framework: React + TypeScript
*   **React** provides a component-driven paradigm with virtual DOM reconciliation, allowing developers to manage the interactive user interface (information panels, search, filters) independently from the heavy WebGL map loop.
*   **TypeScript** enforces static type checking against the API contract schemas (e.g. `SoilObservationSchema`), preventing runtime type matching failures.

### C. Build System: Vite
*   **Vite** is selected over Webpack/CRA. It uses ES modules for hot module replacement (HMR) and utilizes Rollup for optimized production bundling, ensuring sub-second dev server startup and small bundle footprints.

### D. Server State Management: TanStack Query (React Query)
*   Provides robust caching, request deduplication, background prefetching, and automatic retries for location coordinate queries. This isolates API networking states from the local application UI state.

### E. Client State Management: Zustand
*   A lightweight, centralized state management library utilizing a simple hook-based selector model. It prevents React re-render cascades and manages active layer selection, study area boundaries, and panel opening states without context boilerplate.

### F. Styling: Tailwind CSS & Radix UI
*   **Tailwind CSS** provides utility-first styling driven by design tokens (spacing, typography, HSL color palettes).
*   **Radix UI** primitives provide unstyled, accessible UI components (dialogs, accordion, sliders) that can be fully customized using Tailwind utility classes, keeping the UI premium and lightweight.

---

## 2. Directory Structure

```
frontend/
 ├── public/                    # Static public assets (manifest, favicons)
 ├── src/
 │    ├── api/                  # REST client configurations and TanStack Query hook adapters
 │    │    ├── client.ts        # Axios client instance with V1 path prefix and headers
 │    │    └── queries.ts       # React Query hooks for `/v1/soil` and `/v1/health`
 │    ├── assets/               # Static symbols, brand marks, and default icons
 │    ├── components/           # Shared presentation components (inputs, loaders, buttons)
 │    │    ├── chart/           # Vertical layer depth charts (using Recharts or Chart.js)
 │    │    └── ui/              # Radix UI primitives (combobox, panel, popover, tabs)
 │    ├── config/               # Geospatial projections, study area configurations
 │    ├── features/             # Business modules (completely isolated modules)
 │    │    ├── map/             # Map interface, overlay logic, layer control UI
 │    │    ├── info-panel/      # Scientific vertical soil profile display
 │    │    └── search-filters/  # Coordinate entry, bounding boxes, range selectors
 │    ├── map-engine/           # MapLibre GL wrapper, basemaps, custom overlays
 │    ├── routing/              # Route controllers, layout containers
 │    ├── store/                # Zustand global states (layer registry, active pixel, panels)
 │    ├── theme/                # Global design system configuration, variables
 │    └── utils/                # Geometry helpers, unit converters, coordinate parsers
 ├── package.json
 ├── tsconfig.json
 └── vite.config.ts
```

---

## 3. Scientific Separation Constraint

No scientific computations (such as calculating clay/silt ratios, interpolating depth intervals, or deriving WRB dominant classifications) are permitted inside UI view files or page routing controllers.

*   The UI acts strictly as a **presentation layer** for the scientific JSON payloads.
*   Formatting logic (e.g. converting `pH` color codes, parsing coordinates to degrees-minutes-seconds, or formatting depth units) must reside exclusively inside the `utils/` directory and be verified by isolated client unit tests.
