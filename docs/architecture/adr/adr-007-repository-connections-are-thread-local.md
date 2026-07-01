# ADR-007: Repository Connections are Thread Local

## Status
Accepted

## Context
SQLite connections should not be shared across threads. Concurrent access to a single SQLite database connection by multiple threads can lead to operational errors, synchronization bugs, or database locking conflicts. 

## Decision
Each worker thread in the application lifecycle owns its own read-only SQLite connection. Connections are pooled or cached at the thread level, allowing them to be reused safely across multiple requests processed by that same thread.

## Consequences
*   **No Locking**: Read operations bypass synchronization and cross-thread lock contention because no two threads share the same connection.
*   **No Connection Contention**: Rapid concurrent queries avoid waiting for connection locks or database locks.
*   **Safe Concurrent Reads**: Safe, fast concurrent queries.
*   **Easy Replacement**: The thread-local design establishes a clean interface that can be easily replaced by a standard connection pool when migrating to PostgreSQL later.
