# Frontend Performance Plan

This document establishes engineering guidelines and performance budgets to ensure the Global Soil Explorer runs at 60 FPS under all viewport interactions and remains highly responsive on desktop, large monitors, and mobile/tablet displays.

---

## 1. 60 FPS Interaction Strategy

### A. WebGL Layer Management
*   **Source Reuse**: Never remove and re-add MapLibre sources or layers during simple visibility or opacity changes. Use direct canvas paint updates instead:
    ```typescript
    map.setPaintProperty(layerId, 'raster-opacity', opacity);
    ```
*   **Vector Layer Batching**: Group multiple geographic feature lines (e.g. boundary lines, roads) into single sources to reduce WebGL draw call overhead.

### B. CSS Hardware Acceleration
*   All UI panel sliding transitions, fade-ins, and map control overlays must use CSS GPU-accelerated properties (`transform: translate3d(...)` and `opacity`) rather than top/left/height adjustments that trigger browser reflows.

---

## 2. Rendering Optimization & Virtualization

### A. Zustand Selector Model
To prevent React's default render cascades, components must subscribe to slice selectors in the Zustand store:
```typescript
// Component only re-renders if activeCoordinate changes, not when layers list updates
const activeCoordinate = useStore(state => state.activeCoordinate);
```

### B. List Virtualization
When rendering dense layers lists, historical soil profiles, or large administrative searches, use list virtualization (via libraries like `react-window` or `react-virtual`) to limit DOM nodes to the visible viewport rows.

### C. Bundle Splitting & Lazy Loading
*   **Feature-Based Route Chunking**: Map container, scientific charts (which pull in heavy visualization packages like Recharts), and management panels are loaded asynchronously using React lazy imports (`React.lazy`).
*   **Map Engine Chunking**: MapLibre GL core library is separated into a dedicated asynchronous vendor bundle, lowering initial JS parse overhead.

---

## 3. Memory & Hardware Profiles

### A. Canvas Resource Management
To support high-resolution screens (e.g., 4K monitors and Retina displays) without exhausting GPU memory, the map container restricts the canvas backing store resolution when device pixel ratio exceeds 2.

### B. Mobile Constraints
*   **Adaptive Zoom Levels**: Mobile devices are capped at lower max zoom thresholds for heavy raster files, and dynamic vector layer simplifications are increased to reduce client-side protocol buffer memory pressure.
*   **Touch Optimizations**: Click interactions use touch-delay bypasses to ensure coordinate selection feels instantaneous.
