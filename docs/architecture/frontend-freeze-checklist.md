# Frontend Freeze Checklist

This checklist defines the architectural gates and verification steps that must be passed before beginning the frontend code implementation.

---

## 1. Architectural Integrity

- [x] **Technology Justification Complete**: Leaflet vs MapLibre GL, React, Vite, Zustand, and styling stacks are fully evaluated, justified, and selected.
- [x] **Clean Directory Layout Frozen**: Folder layout separates API communication, map engine rendering, utility libraries, theme tokens, features modules, and routing.
- [x] **UI Presentation Pure**: Scientific data processing logic is completely decoupled; UI components act as pure presentation layers of the API contract responses.
- [x] **URL Sync Decoupled**: State sync (coordinates, layers, zoom, profile select) runs through a standard serialization pipeline in the route layer.

---

## 2. WebGIS & Caching Foundation

- [x] **Basemap & Overlay Abstractions Frozen**: Map wrapper interface is defined; dynamic style rules and custom legend layouts are standardized.
- [x] **Study Area Constraints Standardized**: Restricting panning bounds and masking invalid pixels is decoupled from data layer loading.
- [x] **Caching Layer Defined**: Viewport loading, pan-aware pre-fetching, request abort controllers, and Service Worker LRU cache boundaries are mapped.
- [x] **Vector Tile Path Mapped**: Caching and parsing binary `.pbf` tiles is architecturally unified with raster files.

---

## 3. UI Component Readiness

- [x] **Component Layout Specs Complete**: Header, sidebar panel, map view, and scientific info panel containers have clear grid placement rules.
- [x] **Vertical Horizon Chart Specs Frozen**: Y-Axis depth orientation (pointing downwards) and dynamic layer intervals mapping rules are established.
- [x] **Multi-Profile Navigation Defined**: Tabs displaying profile composition percentages and layer switches are specified.
- [x] **Search & Filter Rules Complete**: Inputs for coordinates, taxonomy filters, and range sliders are validated and decoupled from UI states.

---

## 4. Performance & Scalability

- [x] **60 FPS Performance Rules Complete**: GPU acceleration rules (transform/opacity) and source reuse policies are defined.
- [x] **Render Cascade Prevention Defined**: Store subscription selectors and virtualization boundaries are planned.
- [x] **Future Dataset Compatibility Audited**: Unified Domain Adapter interface is defined, proving future SoilGrids and SSURGO inclusion will not disrupt UI code.

---

## 5. Architectural Abstractions & Refinements (milestone-21-frontend-architecture Gates)

- [x] **Plugin Architecture Registry**: Central registries for Dataset, Basemap, Overlay, Renderer, Search, Export, and Analysis Providers are specified. Adding new modules requires no changes to core app code.
- [x] **Event Bus Architecture**: 중앙 Event Bus defined. Decouples modules with typed, standardized events (`CoordinateSelected`, `ObservationLoaded`, `LayerChanged`, etc.).
- [x] **Command Pattern Engine**: State-modifying actions are encapsulated into Command objects supporting execute/undo tracking for history operations.
- [x] **Capability-Driven UI Model**: UI dynamically locks/unlocks features based on the active dataset's registered `DatasetCapabilities` properties rather than using hardcoded checks.
- [x] **Renderer-Independent Architecture**: Core application features call generic `MapRenderer` abstraction layers rather than binding directly to MapLibre GL API, permitting future Cesium or Leaflet transitions.
- [x] **Responsive Layout Manager**: Multi-device viewport configurations (Desktop floating panels, Tablet drawers, Mobile single-panel viewports) are specified.
- [x] **Scientific Display Profiles**: Visual filtering profiles (`Simple`, `Research`, `Agriculture`, `Engineering`, `Developer`) are defined.
- [x] **Decoupled Query Pipeline**: Observes the sequence `User` → `Validation` → `Cache` → `API` → `Adapter` → `Store` → `Presentation`. Direct API fetches from UI components are prohibited.

