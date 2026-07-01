# ADR-002: Domain is Persistence Independent

## Status
Accepted

## Context
In many software systems, domain objects are coupled to ORM frameworks (like SQLAlchemy or Django ORM) or direct database models. This introduces database dependencies into the domain layer, making it hard to express pure scientific invariants, complicating unit testing, and locking the project into a specific database provider or paradigm.

## Decision
The core domain model must remain completely independent of the persistence layer.
*   Domain classes (like `SoilObservation`, `SoilProfile`, `SoilLayer`, etc.) are implemented as standard Python dataclasses with `slots=True` to keep them memory-efficient, lightweight, and framework-agnostic.
*   No ORM decorators, database drivers, SQL connection references, or query methods are allowed inside the `backend/domain` folder.
*   The domain validates its own scientific invariants (e.g. coordinates within valid geographic bounds, composition shares summing to 100%, valid physical property ranges) regardless of where or how the data is stored.

## Consequences
*   **Pure Scientific Code**: Domain code focuses entirely on scientific invariants, and is easy for soil scientists or domain experts to read and review.
*   **Fast Unit Tests**: Testing the domain requires no database setup, mocks, or filesystem access.
*   **Design Freedom**: The core application logic can run in-memory, read from flat files, or fetch data from a cloud API without modifying the domain layer.
