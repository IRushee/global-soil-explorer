# Global Soil Explorer: Map Experience & Controls

This document details geographic canvas interactions, map control behaviors, basemaps transitions, and spatial overlays management.

---

## 1. Map Interaction Spec

Map navigation must run smoothly at **60 FPS** under WebGL:
*   **Smooth Pan**: Map drags must apply momentum damping. Drag release continues panning, decaying to zero speed over 300ms.
*   **Smooth Zoom**: Mouse wheel zoom triggers fractional level changes (increments of 0.25). Pinch-to-zoom on trackpads maps to exponential scale updates.
*   **Double Click**: Center map on clicked coordinate and increase zoom by 1 level.
*   **Keyboard Navigation**:
    *   Arrow keys pan the map by 100px increments.
    *   `+` (Plus) key zooms in by 1 level.
    *   `-` (Minus) key zooms out by 1 level.

---

## 2. Standard Map Controls

| Control | Location | Visiblity | Shortcut | Interaction Flow |
| :--- | :--- | :--- | :--- | :--- |
| **Zoom Controls**| Right Center | Persistent | `+` / `-` | Click plus/minus to step zoom levels. |
| **Compass** | Right Center | Appears if map rotated | `R` | Displays active north arrow. Click to reset bearing to north. |
| **Scale Bar** | Bottom Left | Persistent | None | Scales distance limits dynamically. Adapts unit metric. |
| **Home View** | Right Center | Persistent | `H` | Resets viewport bounds to default active Study Area limits. |
| **Fullscreen** | Right Center | Optional | `F` | Toggle browser fullscreen. |

---

## 3. Basemaps Transitions

Available basemaps: OpenStreetMap (Streets), Satellite, Terrain, Light, Dark, Blank Canvas.
*   **Switching Behavior**: When switching basemaps, the new layer tiles load underneath the active scientific overlays. Fade the old basemap opacity to zero over 150ms while fading the new basemap in to prevent flashing.
*   **Tile Loading Indicator**: If tiles load slowly, display a subtle linear loading bar at the top border of the map container, keeping map interaction responsive.

---

## 4. Layer Interaction Model

Every map overlay must support:
*   **Visibility Toggle**: Checkbox element next to overlay name. Toggle triggers immediate visibility switch on map.
*   **Opacity Slider**: Range selector slider (`0%` to `100%`). Opacity updates instantly on drag.
*   **Ordering Z-Stack**: Re-order layers in the sidebar list. Drag-and-drop rows changes map index stack (respecting the base limits stack defined in the blueprint).
*   **Active Selection Overlay**: When a coordinate is clicked, a bright outline highlights the selected Soil Map Unit (SMU) polygon, keeping it visually distinct from other layers.
