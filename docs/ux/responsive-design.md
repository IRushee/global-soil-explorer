# Global Soil Explorer: Responsive Design Specification

This document defines layout breakpoints and responsive UI adaptations across target device viewports.

---

## 1. Grid Breakpoints

We utilize standard breakpoints for UI layouts adjustments:
*   **Mobile (xs / sm)**: `< 640px` (Portrait smartphones)
*   **Tablet (md)**: `640px - 1024px` (Landscape tablets, small laptops)
*   **Desktop / Laptop (lg / xl)**: `1024px - 1920px` (Standard desktop monitors)
*   **Ultra-wide (2xl)**: `> 1920px` (High-resolution monitors)

---

## 2. Layout Adaptations Matrix

| Component | Mobile (< 640px) | Tablet (640px - 1024px) | Desktop (> 1024px) |
| :--- | :--- | :--- | :--- |
| **Sidebar** | Full-screen drawer, hidden by default. | Slide-out overlay, width 320px. | Collapsible sidebar, fixed 320px width. |
| **Info Panel** | Bottom sheet slider (max 60% viewport height). | Collapsible sidebar, fixed 380px width. | Collapsible sidebar, fixed 380px width. |
| **Map Canvas** | Occupies full background. Gestures lock: pinch zoom, single-finger drag. | Occupies full center. | Occupies full center. |
| **Header Controls**| Icon shortcuts bar only. Selector dropdowns collapsable. | Full selector dropdowns. | Full selector dropdowns. |
| **Tooltips** | Deactivated; replaced by tap selection cards. | Active on click / hover. | Active on hover. |

---

## 3. UI Element Behaviors

*   **Floating Toolbars**: On mobile, floating toolbar buttons wrap into a single bottom dock to prevent canvas clutter.
*   **Table Scroll**: All data tables (such as physical/chemical layer property breakdowns) must scroll horizontally inside a viewport element, using custom scroll bar indicators to avoid layout clipping.
