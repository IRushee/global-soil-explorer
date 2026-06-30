# Database Discovery: HWSD v2.0

---

## Document Metadata
*   **Purpose**: Perform structural discovery and architectural analysis of the `HWSD2.mdb` relational database.
*   **Audience**: GIS database engineers, backend developers, and product leads.
*   **Assumptions**:
    *   The database structure is analyzed in its raw state without modifications.
    *   Scientific interpretation of individual soil attributes is out of scope for this phase.

---

## 1. Database Overview
*   **Database Format**: Microsoft Access Jet Database (`.mdb`).
*   **File Size**: `91,594,752` bytes (~91.6 MB).
*   **Number of Tables**: 25 tables.
*   **Number of Relationships**: None declared in database system metadata (no `MSysRelationships` table found).
*   **Number of Indexes**: 25 primary key indexes and 26 auxiliary column indexes (typically on `CODE` or `HWSD2_SMU_ID` columns).

---

## 2. Table Inventory

The 25 tables within `HWSD2.mdb` are classified into core data tables, schema metadata catalogs, and lookup dictionaries:

### Core Spatial & Attribute Data Tables
1.  **`HWSD2_LAYERS`**
    *   *Purpose*: Primary attribute data table storing physical and chemical properties of soil across vertical depth layers.
    *   *Number of Columns*: 48
    *   *Number of Rows*: 408,835
    *   *Primary Key*: `ID`
    *   *Foreign Keys*: None declared (maps to `HWSD2_SMU` via `HWSD2_SMU_ID`).
2.  **`HWSD2_SMU`**
    *   *Purpose*: Soil Mapping Unit metadata linking spatial map indexes to broad geography and component features.
    *   *Number of Columns*: 23
    *   *Number of Rows*: 29,538
    *   *Primary Key*: `ID`
    *   *Foreign Keys*: None declared (maps to `HWSD2_SMU_ID`).

### Schema Metadata Tables
3.  **`HWSD2_LAYERS_METADATA`**
    *   *Purpose*: Defines the schema, description, and domains for variables in `HWSD2_LAYERS`.
    *   *Number of Columns*: 6
    *   *Number of Rows*: 47
    *   *Primary Key*: `ID`
    *   *Foreign Keys*: None.
4.  **`HWSD2_SMU_METADATA`**
    *   *Purpose*: Defines the schema, description, and domains for variables in `HWSD2_SMU`.
    *   *Number of Columns*: 6
    *   *Number of Rows*: 23
    *   *Primary Key*: `ID`
    *   *Foreign Keys*: None.

### Dictionary Lookup Tables (`D_*`)
These 18 tables store standardized integer-to-string or code-to-label mapping definitions:
*   **`D_ADD_PROP`** (2 cols, 3 rows, Primary Key: `CODE`)
*   **`D_AWC`** (2 cols, 7 rows, Primary Key: `CODE`)
*   **`D_COVERAGE`** (2 cols, 9 rows, Primary Key: `CODE`)
*   **`D_FAO90`** (3 cols, 193 rows, Primary Key: `CODE`)
*   **`D_IL`** (2 cols, 5 rows, Primary Key: `CODE`)
*   **`D_KOPPEN`** (2 cols, 5 rows, Primary Key: `CODE`)
*   **`D_PHASE`** (2 cols, 31 rows, Primary Key: `CODE`)
*   **`D_ROOT_DEPTH`** (2 cols, 4 rows, Primary Key: `CODE`)
*   **`D_ROOTS`** (2 cols, 7 rows, Primary Key: `CODE`)
*   **`D_TEXTURE`** (2 cols, 4 rows, Primary Key: `CODE`)
*   **`D_TEXTURE_SOTER`** (2 cols, 5 rows, Primary Key: `CODE`)
*   **`D_TEXTURE_USDA`** (2 cols, 13 rows, Primary Key: `CODE`)
*   **`D_WRB_PHASES`** (3 cols, 556 rows, Primary Key: `ID`)
*   **`D_WRB2`** (2 cols, 35 rows, Primary Key: `CODE`)
*   **`D_WRB4`** (3 cols, 191 rows, Primary Key: `ID`)
*   **`D_DRAINAGE`** (3 cols, 7 rows, Primary Key: `CODE`)
*   **`D_SWR`** (2 cols, 5 rows, Primary Key: `CODE`)
*   **`D_WRB2code`** (2 cols, 35 rows, Primary Key: `CODE`)

### World Reference Base (WRB) Classification Tables
*   **`WRB_Class`** (9 cols, 34 rows, Primary Key: `ID`)
*   **`WRB_Layer`** (10 cols, 1 row, Primary Key: `ID`)
*   **`WRB_Library`** (3 cols, 1 row, Primary Key: `ID_AezLibrary`)

---

## 3. Database Relationships

There are **no explicit physical relationships or foreign key constraints** defined in the Access database metadata. The database relies entirely on implicit logical joins:

1.  **Spatial to SMU Join**: The coordinates on the map identify a grid cell value in `HWSD2.bil` representing a Map Unit Key. This key is matched to `HWSD2_SMU_ID` in `HWSD2_SMU`.
2.  **SMU to Layer Join**: Both `HWSD2_SMU` and `HWSD2_LAYERS` share the `HWSD2_SMU_ID` column. This field acts as the logical join key to link general mapping unit metadata with specific physical/chemical soil profiles.
3.  **Variable Resolution**: Attribute codes in the data columns of both `HWSD2_SMU` and `HWSD2_LAYERS` map to the `CODE` primary key inside the dictionary (`D_*`) tables to resolve integers into descriptive text (e.g., matching texture code `1` to `Coarse`).

---

## 4. Initial Observations
*   **Lack of Referential Integrity**: Because there are no declared foreign keys or database relationships, data consistency is not enforced at the database layer. This means we must programmatically validate constraints during data migration and processing.
*   **Scale Asymmetry**: `HWSD2_LAYERS` contains over 408,000 rows, making up the vast majority of the database size. All other tables (including mapping units and dictionaries) are relatively small helper datasets.
*   **Redundancies**: There are duplicate dictionary tables (such as `D_WRB2` and `D_WRB2code`) with identical column formats and row counts, indicating structural overlaps.
*   **Self-Documenting Metadata**: The inclusion of `HWSD2_LAYERS_METADATA` and `HWSD2_SMU_METADATA` is highly beneficial. These tables describe the structure of the primary database variables, enabling automated schema definitions.

---

## 5. Questions Remaining

Before performing a detailed analysis of specific table schemas, the following structural questions must be resolved:

1.  **Row Count Discrepancy**:
    *   Why are there 408,835 rows in `HWSD2_LAYERS` compared to only 29,538 rows in `HWSD2_SMU`? 
    *   What combination of columns forms the logical composite key in `HWSD2_LAYERS` to uniquely identify a record (e.g., is there a specific sequence number or layer identifier)?
2.  **Null and Placeholder Values**:
    *   How are missing or unmeasured properties stored in the database tables (e.g., database `NULL` vs. a default numeric flag)?
3.  **Metadata Consistency**:
    *   Do the columns in `HWSD2_LAYERS` and `HWSD2_SMU` match the listings in their respective `METADATA` helper tables exactly?
4.  **Index Optimization**:
    *   Which index columns should be explicitly declared during the SQLite migration to guarantee fast query performance on coordinate queries?
