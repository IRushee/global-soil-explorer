# Product Glossary: Global Soil Explorer

---

## Document Metadata
*   **Purpose**: Define standardized soil science, geospatial, and database-specific terminology to align the product development team and ensure consistent user legends.
*   **Audience**: Product leads, designers, GIS analysts, software developers, and QA engineers.
*   **Assumptions**:
    *   Standardizing scientific and GIS definitions reduces communication gaps between domain scientists and developers.
    *   Using dataset-agnostic terminology helps the glossary remain stable as new datasets are integrated.

---

## 1. Soil Science Terminology

*   **Soil Profile**: A vertical section of the soil from the ground surface down to where it meets the underlying parent rock, displaying distinct horizontal layers.
*   **Soil Horizon**: A distinct layer within a soil profile, running parallel to the soil surface, characterized by specific physical, chemical, or biological properties.
*   **Soil Texture**: The relative proportion of different-sized mineral particles—specifically sand, silt, and clay—present in the soil.
    *   **Sand**: Coarse mineral particles ranging from 0.05 to 2.0 mm in diameter. High drainage, low nutrient retention.
    *   **Silt**: Medium mineral particles ranging from 0.002 to 0.05 mm in diameter. Smooth, floury texture.
    *   **Clay**: Extremely fine mineral particles less than 0.002 mm in diameter. High nutrient and water retention, low drainage.
*   **Soil Acidity (pH)**: A measure of the acidity or alkalinity of the soil solution, affecting nutrient availability and biological activity.
*   **Organic Carbon (OC)**: The carbon component of organic matter (decomposed plant and animal materials) in the soil, serving as a primary indicator of soil health and fertility.
*   **Cation Exchange Capacity (CEC)**: A measure of how much exchangeable cations (nutrients like calcium, magnesium, potassium) the soil can retain, indicating soil nutrient storage capacity.
*   **Salinity**: The concentration of soluble salts in the soil, which can limit plant water uptake at high levels.
*   **Sodicity**: The concentration of sodium in the soil, which can degrade soil structure and reduce water permeability.

---

## 2. Geospatial & Web GIS Terminology

*   **Raster Grid**: A spatial data model that represents geographic features as a grid of cell matrix rows and columns, where each cell contains a specific value (e.g., elevation or pH).
*   **Spatial Resolution**: The physical size of the area on the Earth's surface represented by a single cell in a raster dataset (e.g., 30 arc-seconds corresponds to approximately 1 square kilometer at the equator).
*   **Coordinate Reference System (CRS)**: A coordinate-based local, regional, or global system used to locate geographical entities on the Earth's curved surface.
*   **Attribute Table**: A database table associated with a spatial dataset, where rows represent individual geographic features and columns represent their descriptive characteristics.

---

## 3. Dataset-Specific Concept Mapping

*   **Mapping Unit (MU)**: A defined geographical area on a soil map composed of one or more specific soil types (associations) that share similar landscape characteristics.
*   **Soil Unit (SU)**: A specific, classified soil classification category (e.g., Haplic Luvisol) that resides within a mapping unit.
*   **Depth Intervals (Vertical Layers)**: Designated depth boundaries (e.g., 0–20 cm or 30–100 cm) used to sample, measure, and record vertical variations in soil properties.

---

## 4. References
*   *FAO (Food and Agriculture Organization)* World Reference Base (WRB) for Soil Resources.
*   *Soil Science Society of America (SSSA)* Glossary of Soil Science Terms.
