# Global Soil Explorer: UX Performance Guidelines

This document establishes measurable performance targets and client-side optimization patterns.

---

## 1. Performance Target Metrics

| Metric | Target Value | Verification Method |
| :--- | :--- | :--- |
| **Initial Bundle Load**| `< 2.0 seconds` | Chrome DevTools Lighthouse audit (Fast 3G throttle) |
| **Viewport Redraw Rate**| `60 FPS` | MapLibre benchmark rendering cycles |
| **Interaction Latency**| `< 16 ms` | User action trigger to state re-render check |
| **E2E Click Latency** | `< 150 ms` (cached)<br>`< 500 ms` (uncached) | TanStack Query network duration monitor |

---

## 2. Optimization Rules

*   **Zustand Selector Performance**: UI components must subscribe only to specific state properties using Zustand selectors (e.g. `useGlobalStore(state => state.sidebarOpen)`), preventing unnecessary full-page updates on map center changes.
*   **Table and Panel Virtualization**: Lists of coordinates history, bookmarks, or large measurement tables exceeding 20 rows must use virtualization libraries (e.g. `@tanstack/react-virtual`) to limit the active DOM node count.
*   **Lazy Loading & Code Splitting**: Main panel features (e.g. the PDF export canvas, complex Recharts modules, Turf analysis tools) must be lazy-loaded using React `lazy` and `Suspense` chunk boundaries.
