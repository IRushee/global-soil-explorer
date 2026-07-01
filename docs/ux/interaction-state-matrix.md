# Global Soil Explorer: Interaction State Matrix

This matrix maps key user interactions to their respective system states, loading behaviors, success results, error states, and keyboard/accessibility rules.

---

## 1. Interaction Event Workflows

### A. Coordinate Selection (Map Click)
*   **Trigger**: Single left click / Tap on map coordinate pin.
*   **User Feedback**: Crosshairs flash teal. Marker pin moves to clicked coordinates. Scientific Info Panel slides open.
*   **State Transition**: `selectedCoordinate` store state updates.
*   **Loading State**: Panel displays summary skeletons within 16ms. Progress bar flashes along panel header.
*   **Success State**: Profiles charts render and values populate data tables.
*   **Empty State**: If clicked coordinates fall outside grid bounds, show a clean "No Scientific Records" notice.
*   **Error State**: Displays "Database Query Failure" card inside panel with retry controls.
*   **Keyboard Behavior**: Pressing `Space` / `Enter` when focusing coordinates trigger selections.
*   **Accessibility Behavior**: Screen reader announces: "Coordinate selected at latitude Y, longitude X."

### B. Search Execution
*   **Trigger**: Enter search string in search bar and press `Enter` / click search icon.
*   **User Feedback**: Suggestion autocomplete drawer expands. Match text highlights.
*   **State Transition**: Search status updates in store.
*   **Loading State**: Display a subtle circular loader inside search input field.
*   **Success State**: Suggestions render. Choosing an item dispatches coordinate selection commands and pans map.
*   **Empty State**: Suggestion list shows "No coordinates or taxons found."
*   **Error State**: Input border flashes red. Low-priority toast shows "Geocoder API Unavailable."
*   **Keyboard Behavior**: Up/Down arrow keys highlight suggestions. `Enter` selects. `Esc` closes suggestions.
*   **Accessibility Behavior**: Search suggestions read as combobox nodes with correct aria labels.

### C. Workspace Export
*   **Trigger**: Click CSV/PDF button in export options panel.
*   **User Feedback**: Export loader overlay opens. Download begins on compile complete.
*   **State Transition**: Export status sets to active.
*   **Loading State**: Displays modal loader: "Compiling report...".
*   **Success State**: Modal dismisses. File downloads via browser downloads API. Low-priority toast shows "Export Complete."
*   **Empty State**: If no observation selected, the export buttons remain disabled.
*   **Error State**: Modal closes. Toast shows error details: "PDF compile failed."
*   **Keyboard Behavior**: `Ctrl + E` opens the export panel.
*   **Accessibility Behavior**: Focus locks inside modal dialogue during active compile status.
