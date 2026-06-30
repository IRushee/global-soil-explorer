# User Personas: Global Soil Explorer

---

## Document Metadata
*   **Purpose**: Define the primary user profiles, goals, pain points, workflows, and success criteria to guide product design and user interface layout decisions.
*   **Audience**: Product leads, UX/UI designers, frontend developers, and QA engineers.
*   **Assumptions**:
    *   By designing for these five broad roles, the platform will support both casual educational uses and advanced scientific and engineering workflows.
    *   Providing exportable formats suitable for each persona encourages integration of the platform into existing analytical environments.

---

## 1. Persona Profiles

### 1. The Researcher
*   **Description**: An environmental scientist, agronomist, or academic modeling climate and ecological systems.
*   **Goals**:
    *   Obtain high-fidelity, peer-reviewed soil datasets to feed into crop models, hydrological simulations, or carbon sequestration projects.
    *   Understand the physical and chemical properties of soil across multiple vertical depth levels.
*   **Pain Points**:
    *   Friction in verifying the source, methodology, and uncertainty level of data.
    *   Difficulty extracting vertical depth gradients for precise geological layers.
*   **Typical Workflow**:
    1.  Locate a study area of interest on the globe.
    2.  Extract the coordinate-level or regional soil metrics (e.g., pH, organic carbon) across all available depth intervals.
    3.  Export the raw tabular dataset to integrate with statistical models (e.g., R, Python scripts).
*   **Success Criteria**: Rapid extraction of high-fidelity, multi-layer soil data with clear, citeable scientific provenance.

### 2. The GIS Professional
*   **Description**: A geospatial analyst or cartographer working in government agencies, engineering firms, or conservation organizations.
*   **Goals**:
    *   Integrate global and regional soil datasets with other spatial layers (e.g., elevation, land cover, water systems).
    *   Validate web map layers against local spatial surveys.
*   **Pain Points**:
    *   Struggles with mismatched Coordinate Reference Systems (CRS) and grid alignments.
    *   Large raster files consume massive storage and computing power during processing.
*   **Typical Workflow**:
    1.  Search for compatible soil layers for a specific national or regional bounding box.
    2.  Visually compare web layers with local vector data boundaries.
    3.  Download standardized, cropped spatial files to compile into local GIS project files.
*   **Success Criteria**: Standardized, high-performance spatial layer views with easy bounding-box extraction capabilities.

### 3. The Student
*   **Description**: A university or high school student studying environmental science, geology, agriculture, or geography.
*   **Goals**:
    *   Explore how soil properties change across different climates, topographies, and land use types.
    *   Learn how variables (like soil acidity or texture) impact local ecosystems and agricultural capabilities.
*   **Pain Points**:
    *   Overwhelmed by dense scientific databases, codes, and unformatted data tables.
    *   Lacks the access or training required to use complex desktop GIS applications.
*   **Typical Workflow**:
    1.  Open the web map to view global distributions of basic soil characteristics (e.g., sand/clay fractions).
    2.  Click on distinct geographic regions (e.g., a desert vs. a river valley) to compare soil profile summaries.
    3.  Read explanations of scientific terms via an interactive interface to complete coursework.
*   **Success Criteria**: A highly visual, responsive, and educational interface that simplifies soil taxonomy and database abbreviations.

### 4. The Environmental Planner
*   **Description**: A land management official, conservationist, or agricultural consultant advising on local land use.
*   **Goals**:
    *   Assess land capability and soil suitability for farming, building, or habitat restoration.
    *   Understand the physical limits of local soil layers (e.g., water drainage capability, erosion risks).
*   **Pain Points**:
    *   Translating laboratory soil metrics into practical land capability assessments.
    *   Lacks the time or scripting skills to process raw spatial files in the field.
*   **Typical Workflow**:
    1.  Access the platform on a tablet or mobile device in the field at specific coordinates.
    2.  View the local soil profile sketch and chemical suitability indicators.
    3.  Generate a simple, printable summary PDF report of local soil conditions for landowners or planners.
*   **Success Criteria**: Single-click point summaries and clean, readable visual soil profiles that can be compiled in the field.

### 5. The Developer
*   **Description**: A software engineer or data scientist building external dashboards, agricultural management tools, or data pipelines.
*   **Goals**:
    *   Query spatial soil data programmatically for specific latitude and longitude points.
    *   Integrate standardized soil datasets directly into environmental API services.
*   **Pain Points**:
    *   Lack of clear, documented spatial endpoints for querying spatial data.
    *   Slow, unoptimized query responses that block application loading times.
*   **Typical Workflow**:
    1.  Read the developer API reference for spatial coordinate querying.
    2.  Test API requests using simple coordinates.
    3.  Integrate JSON query responses directly into custom application code.
*   **Success Criteria**: Clear documentation of data structure, high-speed coordinate queries, and standardized output schemas.

---

## 2. References
*   *USDA Natural Resources Conservation Service (NRCS)* user feedback surveys on Soil Survey accessibility and digital tool usability.
