# ADR-012: DatasetManifest Metadata Backbone

## Status
Accepted

## Context
Datasets (HWSD, SoilGrids, SSURGO) vary in their resolution, available measurements, depth intervals, and citation parameters. Scattering these definitions across client-side logic, API endpoints, or database tables leads to inconsistency and validation failures.

## Decision
Every registered dataset must expose exactly one unified **DatasetManifest** record on the backend.
*   The manifest acts as the metadata backbone, housing projection, resolution, depth intervals, license details, and available layers/properties lists.
*   Both backend translators and frontend schemas read this manifest to dynamically adapt validation, export options, and visual styling rules.

## Consequences
*   *Pros*: Standardizes metadata attribution, improves dataset compliance, and simplifies new dataset registration.
*   *Cons*: Changes to dataset metadata require updating the JSON manifest configuration.
