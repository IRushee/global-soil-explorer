# Problem Statement: Global Soil Explorer

---

## Document Metadata
*   **Purpose**: Articulate the core challenges in soil data discovery, accessibility, interpretation, comparison, and analysis workflows to clarify the product's problem space.
*   **Audience**: Product leads, designers, GIS specialists, domain scientists, and developers.
*   **Assumptions**:
    *   Addressing usability and accessibility bottlenecks will expand the utility of digital soil science beyond specialized academic groups.
    *   A technology-agnostic description of these problems allows the core engine and design of the platform to scale as new datasets emerge.

---

## 1. The Core Problems

### 1. Discovery
**The Problem**: Users looking to address environmental, agricultural, or geological questions do not know which global, regional, or local soil dataset is most appropriate for their geographical area, spatial resolution requirements, or scientific purpose.
*   **User Impact**: Researchers and planners often select datasets based on search engine prominence rather than scientific fit, leading to inaccurate models or inefficient study designs.

### 2. Accessibility
**The Problem**: Soil datasets are published in large, complex, and static formats—such as raster grids (e.g., GeoTIFF), relational databases, and multi-gigabyte spatial files. Accessing this information requires desktop GIS software, high-performance local hardware, and programming scripts.
*   **User Impact**: Non-GIS professionals, students, and field planners are effectively locked out of accessing the data. Even GIS specialists experience friction due to the time and effort required to extract simple point or regional data.

### 3. Interpretation
**The Problem**: Soil data attributes are typically stored in database tables using highly technical scientific nomenclature, specialized soil classifications (such as FAO-90 or USDA classifications), and database codes (e.g., shorthand attribute labels).
*   **User Impact**: Users cannot easily interpret what the variables mean (e.g., translating a code like `T_CEC` to "Cation Exchange Capacity of the topsoil") or how values translate to practical land capability without extensive domain knowledge.

### 4. Comparison
**The Problem**: Comparing or layering data from different soil databases is highly difficult. Different soil inventories use varying spatial reference systems, horizontal resolutions, and vertical depth intervals (e.g., some record topsoil/subsoil, while others use discrete centimeter intervals).
*   **User Impact**: Creating a cohesive multi-source spatial model or comparing global predictions with local ground-truth surveys requires significant data restructuring, resampling, and spatial alignment, which introduces errors.

### 5. Workflow
**The Problem**: Converting raw soil data into actionable decision-making insights requires multiple disconnected tools. A user must download the raw files, load them into a GIS database, run point-in-polygon queries to fetch local coordinates, write custom analytical scripts, and use spreadsheet or charting software to visualize properties.
*   **User Impact**: The workflow is slow, error-prone, and relies on manual repetition. Field workers and planners cannot easily perform quick on-site assessments or share interactive findings with stakeholders.

---

## 2. References
*   *Global Soil Partnership (GSP) / FAO* reports highlighting the challenges of digital soil mapping capacity building and technical access barriers in developing nations.
*   *ISRIC - World Soil Information* documentation on WoSIS (World Soil Information Service) standardization and data harmonization barriers.
