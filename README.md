# Global Soil Explorer

---

## Repository Metadata
*   **Purpose**: Act as the repository landing page, introducing the product vision and providing a high-level sitemap for users, developers, and researchers.
*   **Audience**: Open-source contributors, environmental researchers, software developers, GIS professionals, and site visitors.
*   **Assumptions**:
    *   Visitors reading this document are looking for either an overview of the product capabilities or a guide to the repository's source code structure.

---

## 1. Main Content

### Introduction
The **Global Soil Explorer** is an open-source Web GIS platform designed to make complex global soil datasets understandable, explorable, and accessible. Soil is a critical, multi-dimensional foundation of life, agriculture, and global climate systems. However, the scientific spatial data describing it is often locked inside heavy, complex files requiring desktop GIS software. 

This platform bridges the gap, allowing anyone to click any point on the globe and instantly visualize the vertical physical, chemical, and morphological soil properties across multiple depth layers.

### Core Capabilities
*   **Interactive Global Map**: Navigate and visualize soil property variations across the globe.
*   **Localized Point Query**: Search or select coordinates to retrieve instant soil characteristics.
*   **Vertical Soil Profiling**: Render dynamic charts showing how properties (like pH, organic carbon, and texture) change from topsoil down to deep subsoil.

### Repository Map & Documentation Sitemap
This repository is organized into distinct functional directories. Refer to the documentation links below to explore specific areas:

```text
global-soil-explorer/
├── backend/                # Server-side spatial query API engine
├── frontend/               # Interactive map and charting interface
├── data/                   # Dataset cache, processed outputs, and raw metadata
├── scripts/                # Ingestion, processing, and caching scripts
└── docs/                   # Full documentation suite
```

#### Documentation Sitemap

##### Product & Strategy
*   [Product Vision](file:///Users/rushee/Projects/global-soil-explorer/docs/product/vision.md): Long-term tenets and success measures.
*   [Problem Statement](file:///Users/rushee/Projects/global-soil-explorer/docs/product/problem-statement.md): Core challenges in soil GIS discovery, access, and workflows.
*   [User Personas](file:///Users/rushee/Projects/global-soil-explorer/docs/product/personas.md): Broad user profiles (Researchers, GIS Pros, Planners, Students, Developers).
*   [Competitive Analysis](file:///Users/rushee/Projects/global-soil-explorer/docs/product/competitive-analysis.md): Landscape analysis, positioning, and opportunities.
*   [MVP Scope](file:///Users/rushee/Projects/global-soil-explorer/docs/product/mvp.md): Core features, scope limits, and launch criteria.
*   [Product Glossary](file:///Users/rushee/Projects/global-soil-explorer/docs/product/glossary.md): Standard scientific and geospatial terminology.

##### Engineering & Development (To Be Created)
*   **System Architecture**: Visual diagrams and data-flow sequences.
*   **Developer Setup**: Environment configurations and installation instructions.
*   **Science & Datasets**: Preprocessing steps, schemas, and citation guidelines.

---

## 2. References
*   *Open Source Geospatial Foundation (OSGeo)* guidelines on open GIS standards and source repository organization.
