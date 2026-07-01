# Global Soil Explorer: UX Design Principles

This document defines the core user experience principles that must govern all frontend views, interactive dialogs, map states, and workflows.

---

## 1. Minimalistic & Map-First Workspace
*   **The Map is the Canvas**: The geographic map canvas must always occupy the primary layout viewport. UI layers (controls, headers, sidebars) float above or border the canvas. Whitespace and margins should remain wide and empty to draw focus to geographic boundaries.
*   **Progressive Disclosure**: Scientific data must be hidden initially and revealed only in response to explicit coordinates clicks. Detailed tables, chemical plots, and dataset descriptors must remain collapsed by default.

## 2. Fast & Predictable Transitions
*   **Immediate Feedback**: Every user interaction (hover, selection, zoom end) must generate visual feedback within **16 milliseconds**.
*   **Transition Easing**: Linear animations are forbidden. Use smooth bezier easings (`cubic-bezier(0.4, 0, 0.2, 1)`) for UI panel expansion, ensuring movement feels natural.

## 3. Scientific Integrity & Accuracy
*   **No Decorative Soil Coloring**: The global soil layers must not be rendered in bright, arbitrary decorative styles by default. Renders must serve scientific visualization constraints (e.g. Munsell scale soil colors, precise texture scales).
*   **No Faux Interpolations**: The client must not interpolate grid cell boundary limits. If coordinate data is missing or out of coverage, the system must show a clean, descriptive "Outside Study Coverage" empty state rather than guessing.

## 4. Universal Accessibility (WCAG AA)
*   **Dual Interaction Control**: Every action (selection, panning, viewport reset) must be triggerable via keyboard shortcuts and touch gesture loops, not just mouse clicks.
*   **High Contrast & Screen Safety**: Color combinations must satisfy WCAG AA contrast ratios (minimum `4.5:1` for body text, `3:1` for large headers). Color blindness modes (Protanopia, Deuteranopia, Tritanopia) must be supported.

## 5. Capabilities-Driven User Interface
*   **No Hardcoded Exceptions**: UI elements (panels, charts, tabs, selectors) must never make assumptions based on hardcoded dataset IDs (e.g. `if (dataset === 'HWSD')`).
*   **Dynamic UI Feature Toggles**: Features must be activated or deactivated dynamically based on runtime capability flags:
    *   *Dataset Capabilities*: coordinate_query, viewport_rendering, multiple_profiles, multiple_layers, soil_texture, soil_chemistry, hydrology, terrain, 3d, exports, time_series, analysis.
    *   *Renderer Capabilities*: vector_tiles, raster_tiles, point_selection, polygon_selection, hover, terrain, pitch, rotation, opacity, clustering.
    *   *Study Area Capabilities*: country_boundaries, administrative_levels, offline_cache, search, bookmarks, measurements.
*   If a capability flag evaluates to `false`, the associated UI control (e.g. the 3D terrain toggle or depth slider) must be hidden or cleanly disabled.

