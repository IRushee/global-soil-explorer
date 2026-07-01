# ADR-003: SQL Never Shapes the Domain

## Status
Accepted

## Context
A common architectural pitfall is modeling the domain class hierarchy to match the flat relational database schemas. For instance, HWSD v2.0 stores vertical soil layers as flat table rows with columns like `SAND`, `PH_WATER`, `AWC`, etc. Modeling the domain as a flat duplicate of these tables loses the benefits of encapsulation, type safety, and rich nested composition (e.g. wrapping measurement properties under logical physical/chemical/hydraulic categories).

## Decision
Domain models are designed based on logical domain concepts and requirements, not SQL structures:
*   The database representation (e.g. the flat tabular structure of `HWSD2_LAYERS`) is decoupled from the domain object representation.
*   Domain classes are structured hierarchically: a `SoilObservation` contains nested `SoilProfile` instances, which contain `SoilLayer` instances, which contain grouped categories of properties (e.g., `PhysicalProperties`, `ChemicalProperties`, `HydraulicProperties`).
*   The repository adapter is solely responsible for reconstructing this rich hierarchical tree from flat database rows.

## Consequences
*   **Logical Domain Structure**: The code aligns with the actual mental model of a soil scientist (observation -> vertical profiles -> depth-based layers -> distinct measurement groups).
*   **Prevention of Schema Leakage**: Future changes to database schemas (e.g., normalising physical properties into separate tables) will not impact how the Domain or Application layers consume the objects.
