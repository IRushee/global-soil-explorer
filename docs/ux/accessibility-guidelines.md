# Global Soil Explorer: Accessibility Guidelines (WCAG AA)

This document enforces system accessibility specifications to ensure full compliance with WCAG AA guidelines.

---

## 1. Keyboard Navigation & Tab Order

All focusable elements must follow a predictable, logical keyboard path:
1.  **Search Input**: Focus shifts to search bar first. Typing matches suggestions.
2.  **Study Area Selector**: Drop-down menus.
3.  **Dataset Selector**: Drop-down menus.
4.  **Map Controls**: Zoom in, Zoom out, Locate pins.
5.  **Sidebar Layers**: Collapsible folders.
6.  **Scientific Info Panel**: Tabs and collapse buttons.

*   **Keyboard Focus Indicator**: A high-visibility `2px` focus ring using `--accent-teal` color must surround the active focused element. Browser outline default styling overrides are required.

---

## 2. ARIA & Screen Reader Semantics

Core interactive widgets must declare correct ARIA attributes:
*   **Sidebar Collapse Buttons**: `aria-expanded="true|false"`, `aria-controls="layer-sidebar"`.
*   **Scientific Info Panel Tabs**: `role="tablist"`, `role="tab"`, `aria-selected="true|false"`.
*   **Coordinate Pin Markers**: `role="button"`, `aria-label="Coordinate selected at latitude Y, longitude X"`.
*   **Map Canvas Wrapper**: `role="application"`, `aria-label="Interactive soil grid map. Use arrow keys to pan, plus and minus keys to zoom."`.

---

## 3. High-Contrast & Color Blindness Modes

*   **Contrast Targets**: Body copy text contrast must measure `> 4.5:1` against panel backgrounds. Status captions must measure `> 3.0:1`.
*   **Reduced Motion**: If a user has `prefers-reduced-motion` enabled in their operating system settings:
    *   Map flight animations (`flyTo`) must degrade instantly to static transitions (`jumpTo`).
    *   Sidebar slide animations must switch to instant visibility toggling.
*   **Color Bind Renders**: Custom legend configurations must avoid red-on-green visual mappings. Provide alternative hatch styling or patterns overlays.
