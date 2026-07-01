# ADR-004: Dataset Anomalies are Normalized Only Inside Adapters

## Status
Accepted

## Context
Raw scientific datasets often contain data entry anomalies, missing value flags (such as `-9`, `-9.0`, `""`), and placeholder values (such as `"-"` in text columns). If these anomalies are propagated into the Application or Domain layers, the core logic becomes cluttered with check conditions like `if val == -9` or `if val == "-"`. This creates code duplication and invites bugs where a missing value is treated as a real negative number.

## Decision
All dataset anomalies and missing value flags are filtered and normalized inside the repository adapters before the domain model is instantiated:
*   Sentinel numbers like `-9`, `-9.0`, and empty strings are converted to Python `None`.
*   Hyphens and text placeholders are cleaned and mapped to `None` or appropriate defaults.
*   The domain constructors receive clean, type-validated inputs and do not contain database-specific anomaly logic.

## Consequences
*   **Clean Domain Logic**: Domain code does not have to deal with sentinel value comparisons or raw data cleaning checks.
*   **Centralized Normalization**: Issues like dataset anomalies (documented in `docs/verification/hwsd-known-anomalies.md`) are addressed in one single place (the repository implementation).
*   **Predictable Values**: The rest of the codebase can reliably check for missing data using standard Python `None`.
