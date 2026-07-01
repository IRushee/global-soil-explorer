# Frontend Freeze Checklist

This checklist defines the architectural gates and verification steps that must be passed before beginning the frontend code implementation.

---

## 1. Architectural Integrity

- [ ] **Technology Justification Complete**: Leaflet vs MapLibre GL, React, Vite, Zustand, and styling stacks are fully evaluated, justified, and selected.
- [ ] **Clean Directory Layout Frozen**: Folder layout separates API communication, map engine rendering, utility libraries, theme tokens, features modules, and routing.
- [ ] **UI Presentation Pure**: Scientific data processing logic is completely decoupled; UI components act as pure presentation layers of the API contract responses.
- [ ] **URL Sync Decoupled**: State sync (coordinates, layers, zoom, profile select) runs through a standard serialization pipeline in the route layer.

---

## 2. WebGIS & Caching Foundation

- [ ] **Basemap & Overlay Abstractions Frozen**: Map wrapper interface is defined; dynamic style rules and custom legend layouts are standardized.
- [ ] **Study Area Constraints Standardized**: Restricting panning bounds and masking invalid pixels is decoupled from data layer loading.
- [ ] **Caching Layer Defined**: Viewport loading, pan-aware pre-fetching, request abort controllers, and Service Worker LRU cache boundaries are mapped.
- [ ] **Vector Tile Path Mapped**: Caching and parsing binary `.pbf` tiles is architecturally unified with raster files.

---

## 3. UI Component Readiness

- [ ] **Component Layout Specs Complete**: Header, sidebar panel, map view, and scientific info panel containers have clear grid placement rules.
- [ ] **Vertical Horizon Chart Specs Frozen**: Y-Axis depth orientation (pointing downwards) and dynamic layer intervals mapping rules are established.
- [ ] **Multi-Profile Navigation Defined**: Tabs displaying profile composition percentages and layer switches are specified.
- [ ] **Search & Filter Rules Complete**: Inputs for coordinates, taxonomy filters, and range sliders are validated and decoupled from UI states.

---

## 4. Performance & Scalability

- [ ] **60 FPS Performance Rules Complete**: GPU acceleration rules (transform/opacity) and source reuse policies are defined.
- [ ] **Render Cascade Prevention Defined**: Store subscription selectors and virtualization boundaries are planned.
- [ ] **Future Dataset Compatibility Audited**: Unified Domain Adapter interface is defined, proving future SoilGrids and SSURGO inclusion will not disrupt UI code.
