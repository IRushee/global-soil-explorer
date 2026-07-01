# ADR-017: Search Registry Abstraction

## Status
Accepted

## Context
A single search bar must handle multiple query formats: geolocation search, latitude/longitude entry (decimal or DMS), taxonomic term matching, and local bookmark lookups. Hardcoding separate search parsing logic inside the search input component creates messy, unmaintainable code.

## Decision
We enforce a unified **Search Registry Abstraction**.
*   We define a standard `SearchProvider` interface and a central `SearchRegistry`.
*   Various search implementations (Coordinate, Location Geocoder, Scientific Attribute, Bookmarks) register dynamically as search providers.
*   The Search input queries the registry to dispatch requests in parallel, consolidates results into a standard `SearchResultItem` format, and maps them directly to coordinate selection events.

## Consequences
*   *Pros*: Unifies search bar behaviors, simplifies search extensibility, and decouples geocoding APIs.
*   *Cons*: Executing multiple providers in parallel requires robust error handling to prevent single provider failures from blocking all results.
