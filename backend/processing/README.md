# Dataset Processing Module

## Purpose
Transform raw datasets into standardized internal representations for querying.

## Responsibilities
*   Parse raw geospatial raster files.
*   Normalize attribute databases.
*   Build optimized query tables and spatial indexes.
*   Provide dataset-specific adapters to integrate alternative datasets.

## Allowed Contents
*   Dataset adapters (e.g. HWSD, DSMW, SoilGrids, OpenLandMap adapters)
*   Transformation scripts
*   Database schema migrations
*   Validation check tools

## Forbidden Contents
*   Runtime query orchestration
*   Client API controllers
