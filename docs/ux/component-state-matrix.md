# Global Soil Explorer: Component State Matrix

This matrix maps core component details to their responsive layouts, visual hierarchies, and performance rules.

---

## 1. Sidebar (Layer Manager)
*   **Responsive Behavior**:
    *   *Desktop*: Anchored left, fixed 320px width.
    *   *Tablet*: Floating overlay drawer, width 320px. Toggles via Header button.
    *   *Mobile*: Slide-up sheet, full-screen.
*   **Visual Hierarchy**:
    *   Header title `--text-primary` (`Title Medium`), bold.
    *   Layer lists grouped under collapsible folders, indented by 12px (`space-3`).
    *   Layer toggle switch checks: Checkbox elements have high-contrast green states when enabled.
*   **Performance Considerations**: Layer visible toggling updates only the map engine overlays array, preventing page layout re-renders.

---

## 2. Scientific Info Panel
*   **Responsive Behavior**:
    *   *Desktop / Tablet*: Anchored right, fixed 380px width.
    *   *Mobile*: Collapsed to a bottom sheet preview bar. Dragging up expands to a full-screen drawer.
*   **Visual Hierarchy**:
    *   Summary card at the top (coordinates, climate, elevation).
    *   Dominant profile tabs selector. Active tabs are underlined in `--accent-teal`.
    *   Property breakdown data tables and inverted depth charts.
*   **Performance Considerations**: Recharts modules and depth profiles render lazily. Data tables with scroll lists use CSS virtualization to limit DOM node tree size.

---

## 3. Search Autocomplete Combobox
*   **Responsive Behavior**:
    *   *Desktop / Tablet*: Floats in top left, width 400px.
    *   *Mobile*: Expands to occupy full header width when active.
*   **Visual Hierarchy**:
    *   Standard input with search icon on the left, shortcut indicator (`/`) on the right.
    *   Suggestions dropdown list sits directly below input with a subtle drop-shadow (`elevation-2`).
*   **Performance Considerations**: Input triggers are debounced by 250ms, limiting requests to NOMINATIM / search registries.
