# ADR-005: Lookup Dictionaries are Immutable

## Status
Accepted

## Context
Resolving soil taxonomy classifications and limitation codes requires mapping integer keys or short string symbols to full scientific terms (e.g. mapping `ACf` to `Ferric Acrisols`). Accessing database lookup tables (such as `D_WRB4` or `D_KOPPEN`) on every query would introduce N+1 query problems and severely impact latency. However, caching these lookup maps in mutable or poorly managed global states can lead to race conditions, thread safety bugs, or inconsistent behavior under concurrent API requests.

## Decision
Lookup dictionaries are loaded exactly once at startup and treated as strictly immutable:
*   Lookup tables are loaded from SQLite into memory inside the repository adapter constructor (`__init__`).
*   These mappings are stored in standard Python dictionaries.
*   Once loaded, these dictionaries are never written to, updated, or modified by any query thread.
*   They are accessed as read-only lookup structures during row mapping.

## Consequences
*   **High Performance**: Key lookup is a fast O(1) in-memory operation, avoiding round-trips to database files during queries.
*   **Thread Safety**: Since the lookup tables are read-only after construction, they can be safely accessed concurrently by hundreds of threads without mutex locks or synchronization overhead.
*   **Negligible Memory Cost**: Pre-loading all lookup maps has a memory overhead of less than 0.3 MB, which is trivial.
