# ADR-011: First-Class Study Area Abstraction

## Status
Accepted

## Context
Initial implementations often hardcode regional settings (e.g. coordinates bounds for central Europe or India). To make the platform study-area-agnostic, study areas must be treated as configuration metadata rather than hardcoded client logic.

## Decision
We will define `StudyArea` as a first-class backend and frontend model.
*   The backend will expose configuration endpoints: `GET /v1/study-areas` and `GET /v1/study-areas/{id}`.
*   Each `StudyArea` record encapsulates bounds, projections, zoom levels, available datasets, and plugin configurations.
*   The frontend dynamically initializes map camera bounds, layers lists, and geocoder settings based on the active `StudyArea` metadata payload fetched on mount.

## Consequences
*   *Pros*: Eliminates hardcoded regional overrides; permits scaling the explorer to new regions purely via database configurations.
*   *Cons*: Adds coordinate queries overhead on client mount to fetch study area bounds.
