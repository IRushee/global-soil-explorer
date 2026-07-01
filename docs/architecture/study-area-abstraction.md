# Study Area Abstraction Specification

This document details the architectural design for the generic `StudyArea` abstraction in the Global Soil Explorer. This abstraction enables queries over arbitrary geographic boundaries (points, bounding boxes, polygons, administrative regions) and outlines the clipping and statistical aggregation pipelines.

---

## 1. Core Abstraction Interface

The `StudyArea` is a dataset-agnostic boundary interface defining coordinate containment and raster masking policies.

```python
from abc import ABC, abstractmethod
from typing import Generator
from backend.domain import Coordinate

class StudyArea(ABC):
    """Abstract base class representing a geographic Area of Interest (AOI)."""

    @property
    @abstractmethod
    def bounding_box(self) -> tuple[float, float, float, float]:
        """Return the bounding box as (min_lat, min_lon, max_lat, max_lon)."""
        pass

    @abstractmethod
    def contains(self, coordinate: Coordinate) -> bool:
        """Verify if a coordinate lies within the boundaries of this StudyArea."""
        pass

    @abstractmethod
    def get_grid_mask(self, cell_size_deg: float) -> Generator[tuple[int, int], None, None]:
        """Generate grid cell indices (col, row) intersecting this study area."""
        pass
```

---

## 2. Concrete StudyArea Implementations

1. **`BoundingBoxStudyArea`**: Defined by minimum and maximum latitude/longitude pairs. Highly performant since inclusion checks are simple numeric range comparisons.
2. **`PolygonStudyArea`**: Defined by a list of outer (and optional inner) vertices. Utilizes the Ray Casting algorithm (Point-in-Polygon) to verify coordinate containment.
3. **`AdministrativeStudyArea`**: Resolves boundaries using standard ISO country/state/district codes by querying a simplified geometries vector database (e.g. Natural Earth dataset).
4. **`UploadedGeometryStudyArea`**: Dynamically constructs boundaries by parsing standard GIS file uploads (GeoJSON, WKT, or Shapefiles).

---

## 3. Zonal Statistics Processing Pipeline

To analyze soil properties over a `StudyArea` (e.g., computing the average sand content or dominant soil type in a watershed), the system utilizes a Zonal Statistics pipeline:

```
[StudyArea Geometry] 
        │
        ▼
[Calculate Bounding Box] 
        │
        ▼
[Clip Raster Grid to Bounding Box] 
        │
        ▼
[Filter Cells using get_grid_mask()] 
        │
        ▼
[Batch Seek Raster Coordinates] ──> [Query SQLite for SMU Profile Data]
        │
        ▼
[Compute Weighted Area Aggregates (Mean / Mode / Median)]
```

### Zonal Aggregation Mathematical Formulation
*   **Mean Property Value** (e.g., average organic carbon):
    $$\bar{P} = \frac{\sum_{i=1}^{N} (P_i \times W_i)}{\sum_{i=1}^{N} W_i}$$
    Where $P_i$ is the property value of grid cell $i$, and $W_i$ is the composition share (area weight) of that profile.
*   **Dominant Soil Class (Mode)**:
    $$C_{dominant} = \operatorname{arg\,max}_{c \in Classes} \sum_{i=1}^{N} \text{Area}_i(c)$$

---

## 4. Integration into the Application Architecture

The `StudyArea` interacts with the backend components via a new query coordinator service:

*   **`ZonalStatisticsService`**:
    *   Accepts a `StudyArea` object and a target `PropertyType`.
    *   Uses `StudyArea.get_grid_mask` to resolve cells.
    *   Batches the resulting cells to `SpatialLookupService` to retrieve mapping units (`SMU_IDs`).
    *   Performs database joins on the SQLite table to aggregate parameters.
    *   Returns structured statistical snapshots (min, max, mean, standard deviation, and histograms) without modifying existing domain objects.
