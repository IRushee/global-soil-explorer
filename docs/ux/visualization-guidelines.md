# Global Soil Explorer: Scientific Visualization Guidelines

This document establishes standard visual layouts, color rules, and charting guidelines for scientific soil measurements.

---

## 1. Soil Profile Visual Horizons

*   **Vertical Horizon Column**: Display soil layers as a vertical stack with relative layer depths (e.g. 0-10cm, 10-30cm, 30-60cm) mapped to scale.
*   **Scientific Color Representation**:
    *   Do not use decorative colors for layer horizons.
    *   Horizontal blocks must utilize colors representing actual soil properties (e.g. organic carbon content gradient, clay share percentage gradient, or resolved Munsell color if provided in metadata).
    *   Provide clear color scales (legends) next to columns indicating range parameters (e.g. light brown to dark brown for organic carbon ranges: `0 g/kg` to `120 g/kg`).

---

## 2. Scientific Property Charting

*   **Depth Profiles (Y-Axis Inverted)**:
    *   When plotting properties against depth (e.g. pH or clay % vs depth in cm), the **depth axis (Y-axis) must be inverted** (0cm at the top, increasing downward to 100cm/200cm).
    *   The property value is plotted on the horizontal X-axis.
*   **Property-vs-Property Plots**:
    *   Line charts must use clean, solid lines (`stroke-width: 2px`) with coordinate dots on hover.
    *   Avoid complex grid patterns. Use subtle horizontal reference grid lines.

---

## 3. Dynamic Legend Conventions

*   Legends must display range steps clearly.
*   All scientific units must conform to the **Scientific Attribute Catalog** values:
    *   Clay / Sand / Silt: `%` (percentage share values).
    *   Organic Carbon: `g/kg` (grams per kilogram).
    *   pH: pH scale units (standard color spectrum from red [acidic] to green [neutral] to purple [alkaline]).
    *   Total Nitrogen: `g/kg`.
