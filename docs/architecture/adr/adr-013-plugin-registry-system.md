# ADR-013: Plugin Registry System

## Status
Accepted

## Context
Adding new renderers, dataset translators, analysis tools, or file exporters should not require altering the application's core rendering loop or coordinate pipelines. The core must remain stable and locked.

## Decision
We enforce a centralized **Plugin Registry System**.
*   Core services and components interact only with generic interface abstractions.
*   Concrete custom features are registered dynamically as plugins (implementing predefined interfaces) during application startup.
*   The application core exposes registry methods (`register`, `get`, `list`) to discover active extensions.

## Consequences
*   *Pros*: Protects the codebase core from regression errors when adding new features; allows developer teams to build plugins independently.
*   *Cons*: Requires strict interface contracts.
