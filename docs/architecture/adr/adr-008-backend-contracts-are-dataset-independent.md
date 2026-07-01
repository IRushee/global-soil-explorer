# ADR-008: Backend Contracts are Dataset Independent

## Status
Accepted

## Context
The Global Soil Explorer platform is initially built on top of the Harmonized World Soil Database (HWSD v2.0). However, the long-term goal of the project is to build a dataset-agnostic architecture that can support alternative global or national soil datasets (e.g., ISRIC SoilGrids, USDA SSURGO) without modifying the client interface or breaking API consumers. If the public API contracts leak HWSD-specific codes, database structures, or column constraints, any dataset upgrade or replacement will ripple across the entire system.

## Decision
All backend contracts (including endpoint routing, query models, and response serialization schemas) must represent abstract, pure scientific concepts.
*   No dataset-specific codes, relational primary/foreign keys, or table abbreviations (e.g., SQLite `MU_GLOBAL` or column name shortcuts) will be exposed in request parameters or response models.
*   Data points are grouped logically under standard scientific concepts (e.g., physical, chemical, and hydraulic properties) with explicit, human-readable descriptors.
*   Units conform to international standards (e.g., %, dS/m, cmol(+)/kg) rather than raw database field encodings.

## Consequences
*   **Decoupled Frontend**: Clients can render maps, graphs, and profile cards based on a stable scientific interface, completely insulated from dataset shifts.
*   **Interoperability**: Migrating or adding support for new datasets (e.g., SSURGO) only requires writing a new repository adapter; no API layer or routing changes are needed.
*   **Scientific Integrity**: The system terminology aligns with international standards, making the API intuitive and valuable to soil scientists and external integrations.
