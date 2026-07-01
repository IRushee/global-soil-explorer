# ADR-010: ConfigurationService Architecture

## Status
Accepted

## Context
Various application components need runtime environment values, feature flags, and active settings (active study area, active dataset). Reading environment variables (`process.env`) or global browser structures (`window.config`) directly across different layout files creates tight coupling and breaks testing isolation.

## Decision
We will enforce a unified **ConfigurationService** as the sole source of truth for runtime configurations. 
*   All environment variable parses and settings fetches are encapsulated inside this service.
*   Application modules, components, and hooks must inject this service to query configuration parameters.
*   Direct access to environment variables outside infrastructure bootstrap files is strictly prohibited.

## Consequences
*   *Pros*: Unifies configuration parsing, simplifies mock injection during testing, and enables dynamic feature flagging.
*   *Cons*: Requires dependency injection boilerplate across layers.
