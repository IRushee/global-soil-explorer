# ADR-009: Response Models Never Expose Persistence Concepts

## Status
Accepted

## Context
When serialized JSON responses are generated directly from or shaped by database models, storage-layer concepts (such as auto-incrementing integer IDs, SQL join tables, indexing metadata, or file paths) leak to the public API client. This tight coupling makes the client dependent on the specific storage technology and database layout, violating clean architecture principles and hindering migration (e.g., from SQLite to a distributed document store or PostGIS).

## Decision
Response serialization schemas (Pydantic models) will represent only the scientific domain structure, completely decoupled from persistence concepts:
*   No database-specific identifiers, sequential table keys, or raw storage indices will be returned in responses.
*   The response structure is organized hierarchically around physical vertical profiles and depth layers, rather than normalized relational table schemas.
*   Metadata is presented purely as scientific provenance (e.g., active database description and source versioning) rather than database filename paths or connection states.

## Consequences
*   **Insulated Client**: The client remains completely unaffected if the backend transitions from SQLite/PostGIS to a document database (e.g., MongoDB) or a vector tiling service.
*   **Improved Security**: No internal database structures or schema details are leaked in API responses, reducing the exposure surface.
*   **Cleaner Client Code**: The client works with domain-specific concepts (e.g., `profiles`, `layers`, `measurements`) instead of parsing relational junction table fields.
