# Global Soil Explorer: Interaction Guidelines

This document specifies standard interaction feedback loops, states transitions, and focus controls across the WebGIS application.

---

## 1. Interaction State Guidelines

Every UI component must support the following states:

*   **Default State**: Standard outline. Border `1px`, color `--border-subtle`. Text `--text-primary`.
*   **Hover State**: Border shifts to `--accent-teal` or lightens by 10%. Scale transforms by 101% over 80ms. Cursor pointer.
*   **Active/Pressed State**: Shift background color to a darker variant (e.g. darken by 15%). Scale transforms by 99% to indicate click pressure.
*   **Disabled State**: Opacity reduced to `40%`. Event listener triggers deactivated. Cursor `not-allowed`.
*   **Focus State**: Focus ring must be visible. Enforce solid `2px` focus ring using `--accent-teal` with `2px` offset.

---

## 2. Notification Workflow

Notifications are governed by priority:

*   **Low Priority (Toasts)**: Non-intrusive card floats in the bottom right corner (e.g. "Coordinate copied to clipboard"). Auto-dismisses in **3 seconds**.
*   **Medium Priority (Status Alerts)**: Inline banner at the top of the Sidebar panel (e.g. "Network Offline. Operating in local read-only cache mode"). Persistent until resolved.
*   **High Priority (Blocking Dialogs)**: Modal centered in the viewport with backdrop blur overlay (e.g. "Dataset Load Failure"). Requires user action to close.

---

## 3. Micro-Interactions

*   **Map Canvas Mouse Move**: If hoverable elements (e.g. custom drawn area limits) are active, crosshairs change to pointers. Tooltip reveals lat/lon in status bar within 16ms.
*   **Sidebar Toggle Click**: Clicking the collapse tab slides the sidebar out of the viewport. The map canvas triggers automatic resize within 200ms to adapt to new bounds width.
