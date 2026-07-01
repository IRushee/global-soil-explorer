# Global Soil Explorer: Scientific Information Panel Layout

This document defines the interface component layout of the main Scientific Information Panel.

---

## 1. Information Panel Hierarchy

To ensure clean layout displays across all screen dimensions, the panel coordinates progressive disclosure:

```
┌────────────────────────────────────────────────────────┐
│                   Information Panel                    │
├────────────────────────────────────────────────────────┤
│  Summary Section (Coord, Weather, Koppen Climate)      │
├────────────────────────────────────────────────────────┤
│  Profile Tabs selector (Dominant share percentage)     │
├────────────────────────────────────────────────────────┤
│  Layout Grid:                                          │
│  ┌─────────────────────────┬────────────────────────┐  │
│  │  Vertical Horizon Chart │ Measurements Tables    │  │
│  │  (Depth vs Properties)  │ ├── Physical properties│  │
│  │                         │ ├── Chemical parameters│  │
│  │                         │ └── Hydraulic stats    │  │
│  └─────────────────────────┴────────────────────────┘  │
├────────────────────────────────────────────────────────┤
│  Context Card:                                         │
│  ├── Hydrologic context descriptions                   │
│  └── Land limitations growth modifiers                 │
├────────────────────────────────────────────────────────┤
│  Metadata & Provenance attribution card                │
├────────────────────────────────────────────────────────┤
│  Related Datasets recommendation links                 │
├────────────────────────────────────────────────────────┤
│  Export Toolbox (JSON, CSV, PDF, Share link triggers)  │
└────────────────────────────────────────────────────────┘
```

---

## 2. Section Expand/Collapse Behaviors

*   **State Retention**: The panel must cache the expansion state (`expanded: true|false`) for each sub-card in local browser storage. If a user expands "Hydrologic Context", it must remain expanded when the user clicks a new map coordinate.
*   **Horizontal Layout Grid**: On large desktop screens, the panel maps details in two adjacent columns (Vertical Horizon Chart on the left, Property tables on the right). On tablet/mobile screens, the layout folds into a single vertical stack, with the chart appearing above the tables.
