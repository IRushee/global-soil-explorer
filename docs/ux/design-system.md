# Global Soil Explorer: Design System Specification

This document lists the official design tokens and styling guidelines for the Global Soil Explorer user interface.

---

## 1. Typography System

*   **Primary Font Family**: Inter, sans-serif (system fallbacks: Segoe UI, Roboto).
*   **Mono Font Family**: JetBrains Mono, monospace (system fallbacks: SFMono-Regular, Consolas).
*   **Scale Hierarchy**:
    *   `Display 1`: `font-size: 32px`, `line-height: 120%`, `font-weight: 800` (Main landing title only)
    *   `Title Large`: `font-size: 20px`, `line-height: 130%`, `font-weight: 700` (Header names, major panels)
    *   `Title Medium`: `font-size: 16px`, `line-height: 140%`, `font-weight: 600` (Card titles, sidebar categories)
    *   `Body Regular`: `font-size: 14px`, `line-height: 150%`, `font-weight: 400` (Default tables, summaries text)
    *   `Caption Mono`: `font-size: 12px`, `line-height: 140%`, `font-weight: 500` (Status bar, coordinates, dataset version numbers)

---

## 2. Spacing & Grid System

We enforce a strict 8px spacing grid:
*   `space-1`: 4px (tight inline padding, badge margins)
*   `space-2`: 8px (standard margins inside buttons, icon labels spacing)
*   `space-3`: 12px (intermediate padding for headers and layout items)
*   `space-4`: 16px (standard card padding, internal panel spacing)
*   `space-6`: 24px (margins between layout divisions)
*   `space-8`: 32px (outer margin gaps)

---

## 3. Color Palette

### A. Core UI Themes

| Token Name | Dark Theme Value (HSL) | Light Theme Value (HSL) | Purpose |
| :--- | :--- | :--- | :--- |
| `--bg-main` | `hsl(222, 47%, 11%)` | `hsl(210, 20%, 98%)` | Primary layout backdrop |
| `--bg-panel` | `hsl(222, 47%, 15%)` | `hsl(0, 0%, 100%)` | Sidebars, drawers, toolbars |
| `--border-subtle`| `hsl(222, 47%, 20%)` | `hsl(214, 32%, 91%)` | Row borders, dividers |
| `--text-primary` | `hsl(210, 40%, 98%)` | `hsl(222, 47%, 15%)` | Body copy, default titles |
| `--text-muted` | `hsl(215, 20%, 65%)` | `hsl(215, 16%, 47%)` | Subtitles, labels, footers |
| `--accent-teal` | `hsl(170, 78%, 45%)` | `hsl(172, 66%, 40%)` | Coordinate pins, selections |

### B. High Contrast Theme
*   Background: `#000000` (Dark) / `#FFFFFF` (Light)
*   Primary Text: `#FFFFFF` (Dark) / `#000000` (Light)
*   Borders: Solid 2px `#FFFFFF` or `#000000`.

---

## 4. Corner Radius & Elevation

*   `radius-sm`: 4px (Buttons, badges)
*   `radius-md`: 8px (Search bars, drop-down menus)
*   `radius-lg`: 12px (Collapsible panels, dialogs)
*   `elevation-1` (Subtle): `box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)`
*   `elevation-2` (Floating Panels): `box-shadow: 0 4px 6px rgba(0,0,0,0.16), 0 2px 4px rgba(0,0,0,0.12)`
*   `elevation-3` (Modal Dialogs): `box-shadow: 0 10px 20px rgba(0,0,0,0.19), 0 6px 6px rgba(0,0,0,0.23)`

---

## 5. Animation Spec

*   **UI Slide In/Out (Sidebar Panels)**: `duration: 250ms`, `easing: cubic-bezier(0.4, 0, 0.2, 1)`
*   **Fade/Reveal (Tooltips, Drop-downs)**: `duration: 150ms`, `easing: ease-out`
*   **Map Transitions (FlyTo center)**: `duration: 1200ms` (dynamic based on distance), `easing: cubic-bezier(0.25, 1, 0.5, 1)`
