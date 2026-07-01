# Navigation & Routing Specification

This document defines the client-side routing model, view navigation states, URL parameter serialization, and accessibility hotkeys.

---

## 1. URL State Synchronization

To support bookmarking, sharing, and reproducibility, the entire application viewport and active query state is serialized in the browser's URL query string.

### URL Schema
`https://explorer.soil.org/map?lat=<latitude>&lon=<longitude>&z=<zoom>&layers=<active_layers>&profile=<profile_index>`

*   **`lat` / `lon`**: Decimal coordinates of the map center or active query pin.
*   **`z`**: Floating-point zoom level of the map camera.
*   **`layers`**: Comma-separated list of active overlay layer IDs (e.g., `hwsd2_smu,koppen_climate`).
*   **`profile`**: Integer index pointing to the active profile selected in the information panel.

### Sync Lifecycle
1.  **Map Pan/Zoom**: Pushing updated lat/lon/z coordinates to URL query string using non-history-polluting state pushes (`history.replaceState`).
2.  **Point Click**: Click updates the active coordinate state and pushes to URL.
3.  **Initial Load**: App parses URL parameters on mount and initializes map camera position and triggers query for coordinates.

---

## 2. Keyboard Navigation Shortcuts

To maximize accessibility for field scientists and power users, the following keyboard navigation shortcuts are registered globally:

| Keyboard Shortcut | Context | Action |
| :--- | :--- | :--- |
| **`Esc`** | Any | Close open drawers/panels; clear active query coordinate selection |
| **`Ctrl + F`** or **`/`** | Map View | Focus coordinate search box |
| **`L`** | Map View | Toggle Sidebar Layer Manager panel |
| **`Tab`** | Info Panel | Cycle through profile tabs (when multiple profiles exist) |
| **`1` - `9`** | Info Panel | Quick-switch to corresponding profile layer depth interval |
| **`Arrow keys`** | Map View | Pan map camera North / South / East / West |
| **`+`** / **`-`** | Map View | Zoom camera in / out |
| **`Spacebar`** | Map View | Drop query pin at the current map center crosshairs |
| **`Ctrl + P`** | Info Panel | Trigger print/export layout for active soil observation report |
