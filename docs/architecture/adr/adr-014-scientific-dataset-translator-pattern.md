# ADR-014: Scientific Dataset Translator Pattern

## Status
Accepted

## Context
Exposing database-specific schemas or raw coordinates SEEK parameters (such as `HWSD2_SMU_ID` or specific column names) directly to the domain layer locks the codebase to one database. A translation layer is required to bridge the gap.

## Decision
We enforce the **Scientific Dataset Translator** pattern.
*   The translator is a dedicated class that isolates raw database query rows and handles key/attribute conversions (e.g. mapping `HWSD2_SMU_ID` to scientific identifiers like `SMU_ID`).
*   It decodes raw coded cells using lookup tables and constructs standard, type-safe Domain models (`SoilObservation`).
*   It operates independently of the core repository interfaces.

## Consequences
*   *Pros*: Standardizes database-to-domain mapping, protects domain model purity, and simplifies support for new datasets.
*   *Cons*: Adds minor serialization mapping steps.
