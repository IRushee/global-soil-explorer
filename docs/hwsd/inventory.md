# Dataset Inventory: HWSD v2.0

---

## Document Metadata
*   **Purpose**: Perform a physical and conceptual inventory of the raw Harmonized World Soil Database (HWSD) v2.0 files.
*   **Audience**: GIS analysts, developers, and product leads.
*   **Assumptions**:
    *   The raw files are located exactly under `data/raw/hwsd/` and have not been altered or modified.
    *   No external preprocessing has been applied to the binary or relational database elements.

---

## 1. Dataset Summary
*   **Dataset Name**: Harmonized World Soil Database (HWSD)
*   **Version**: v2.0
*   **Coordinate Reference System (CRS)**: GCS_WGS_1984 (EPSG:4326)
*   **Spatial Resolution**: 30 arc-seconds (~1 km at the equator)
*   **Raster Dimensions**: 21,600 rows by 43,200 columns (933,120,000 total pixels)
*   **Geographic Extent**:
    *   Longitude: -180.0 to +180.0 degrees
    *   Latitude: -90.0 to +90.0 degrees
*   **Pixel Data Type**: 16-bit Unsigned Integer (UNSIGNEDINT)
*   **NoData Value**: 65535 (used for oceans, lakes, glaciers, and unmapped territories)

---

## 2. File-by-File Inventory

### 1. `HWSD2.bil`
*   **Filename**: `HWSD2.bil`
*   **Exact File Size**: `1,866,240,000` bytes (exactly 1.866 GB)
*   **File Format**: Binary Band Interleaved by Line (BIL) raster grid.
*   **Purpose**: Contains the spatial pixel matrix representing the global distribution of soil mapping units. Each pixel is an index key pointing to the database.
*   **Essential or Optional**: **Essential**
*   **Created By**: FAO & IIASA (compiled from global, regional, and national soil databases).
*   **Can it be regenerated?**: **No**. This contains the primary raw spatial research data.
*   **Dependencies**: Requires `HWSD2.hdr` and `HWSD2.prj` to be correctly parsed and projected by GIS libraries.
*   **Used by our application?**: **Yes**. Used in backend processing to resolve coordinates to map unit IDs.
*   **Notes**: Due to its large size, this file will be excluded from version control (Git) and requires spatial lookup optimizations for web APIs.

### 2. `HWSD2.hdr`
*   **Filename**: `HWSD2.hdr`
*   **Exact File Size**: `338` bytes
*   **File Format**: Plain text ASCII (Header).
*   **Purpose**: Stores the layout metadata (NROWS, NCOLS, data type, bounding box, byte order) of the raw binary `.bil` file.
*   **Essential or Optional**: **Essential**
*   **Created By**: ESRI ArcMap / GIS compilation tools.
*   **Can it be regenerated?**: **Yes**. We can manually reconstruct this file if the grid parameters and byte layout are known.
*   **Dependencies**: `HWSD2.bil` (specifically describes its data boundaries and block layout).
*   **Used by our application?**: **Yes**. Read by spatial engines (GDAL/Rasterio) to structure the stream reading of `HWSD2.bil`.
*   **Notes**: Crucial for file read offsets. Any changes to row/column listings will corrupt pixel coordinate lookups.

### 3. `HWSD2.prj`
*   **Filename**: `HWSD2.prj`
*   **Exact File Size**: `146` bytes
*   **File Format**: Plain text Well-Known Text (WKT) projection format.
*   **Purpose**: Defines the Coordinate Reference System (CRS) for mapping raster grid indexes onto Earth locations.
*   **Essential or Optional**: **Essential**
*   **Created By**: ESRI / GIS compilation tools.
*   **Can it be regenerated?**: **Yes**. Can be recreated using standard WKT strings for GCS WGS 1984.
*   **Dependencies**: `HWSD2.bil` (tells GIS clients what coordinates the grid matches).
*   **Used by our application?**: **Yes**. Validates that coordinate queries map to WGS 84 space.
*   **Notes**: The coordinate system is unprojected (decimal degrees), meaning input GPS coordinates require no math transformations to search the grid.

### 4. `HWSD2.stx`
*   **Filename**: `HWSD2.stx`
*   **Exact File Size**: `64` bytes
*   **File Format**: Plain text ASCII statistics.
*   **Purpose**: Stores pre-calculated band statistics (minimum, maximum, mean, standard deviation) for the raster grid.
*   **Essential or Optional**: **Optional**
*   **Created By**: ESRI / GIS compilation tools.
*   **Can it be regenerated?**: **Yes**. Can be calculated dynamically by reading the values inside `HWSD2.bil`.
*   **Dependencies**: `HWSD2.bil`.
*   **Used by our application?**: **No**. The runtime API query engine does not use raster band summaries.
*   **Notes**: Can be ignored or deleted safely without impacting spatial lookups.

### 5. `HWSD2.mdb`
*   **Filename**: `HWSD2.mdb`
*   **Exact File Size**: `91,594,752` bytes (~91.6 MB)
*   **File Format**: Microsoft Access Database (Jet database engine format).
*   **Purpose**: Relational database storing tabular soil properties (physical, chemical, morphological) across 7 vertical depth layers.
*   **Essential or Optional**: **Essential**
*   **Created By**: FAO & IIASA.
*   **Can it be regenerated?**: **No**. Contains the primary scientific database attributes.
*   **Dependencies**: None.
*   **Used by our application?**: **Yes** (indirectly). The contents will be migrated to a SQLite database for application runtimes.
*   **Notes**: Microsoft Access drivers are not supported natively in Unix/Linux developer environments, necessitating a preprocessing conversion step.

---

## 3. File Relationships

The files interact in a strictly defined geospatial-to-relational lookup sequence:

1.  **Coordinate Verification**: The system reads `HWSD2.prj` to verify that the query coordinate system aligns with the WGS 84 spheroid (in decimal degrees).
2.  **Byte Alignment**: The GIS engine reads `HWSD2.hdr` to retrieve the layout configurations (identifying the Intel byte order, grid dimensions of $21,600 \times 43,200$, and 16-bit integer pixel depth).
3.  **Spatial Index Lookup**: The engine uses the layout rules from `HWSD2.hdr` to compute the cell position from GPS coordinates, reading the specific pixel value at that offset in `HWSD2.bil`. This pixel value is the Map Unit Key (represented as `MU_GLOBAL`).
4.  **Tabular Join**: The application uses the extracted `MU_GLOBAL` key to perform a database query against the relational tables in `HWSD2.mdb` (or its migrated SQLite equivalent), returning the soil layer attributes matching that key.
5.  **Statistics Separation**: `HWSD2.stx` is a standalone metadata log of the raster and does not participate in the runtime coordinate lookup sequence.

---

## 4. Questions Remaining

Before inspecting the MDB contents, the following questions must be resolved during technical research:

1.  **MDB Internal Table Names & Layout**:
    *   What are the exact table names inside `HWSD2.mdb`?
    *   Which table holds the master list of `MU_GLOBAL` keys?
    *   How are the 7 vertical layers stored (e.g., repeating columns per record or multiple rows linked to a single `MU_GLOBAL`)?
2.  **MDB Migration Tools on Unix**:
    *   What command-line utilities (e.g., `mdbtools`, `pandas`, or specific Python packages) are installed and available on our macOS dev environment to extract tables from `.mdb` without MS Access?
3.  **Raster Query Performance**:
    *   Does GDAL or Rasterio suffer performance issues reading directly from raw `.bil` formats under high concurrent requests?
    *   Is there a demonstrated performance benefit in converting the `.bil` raster to a Cloud-Optimized GeoTIFF (COG) during the processing phase?
4.  **Database Mapping Consistency**:
    *   Are there grid values in `HWSD2.bil` that do not exist in `HWSD2.mdb`?
    *   How are `NoData` areas (65535) represented in the database tables, and how should our backend API handle them?
