# ADR-001: Repository Owns Persistence Translation

## Status
Accepted

## Context
When loading data from a persistent store (like an SQLite database or Microsoft Access database), the raw format of the data (relational rows, tables, database-specific type codes) does not match the clean, rich object graph defined by our domain models. If other layers (Application, API, or Domain itself) are responsible for mapping database rows or fields into objects, database structure leaks into those layers. This violates the clean architecture boundary and makes it difficult to change persistence mechanisms.

## Decision
The repository implementation (e.g., `SQLiteSoilObservationRepository`) owns the translation from persistent representation to rich domain representation. 
*   All querying, column name checking, database rows grouping, type conversion, and handling of missing fields occur strictly inside the repository adapters.
*   The repository returns a fully constructed, valid domain object (`SoilObservation`) through the generic interface contract.

## Consequences
*   **Decoupled Application Layer**: The Application layer remains thin, clean, and completely unaware of sqlite3 types or row formats.
*   **Unit Testability**: The domain model can be tested independently of any database connection.
*   **Adaptability**: Changing the database schema or migrating to another database engine (e.g. PostgreSQL) only requires modifying the repository adapter implementation.
