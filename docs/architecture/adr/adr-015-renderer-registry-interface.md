# ADR-015: Renderer Registry Interface

## Status
Accepted

## Context
Tying the frontend layouts, coordinates clicks, and search features directly to a specific WebGIS engine (like MapLibre GL JS) makes it difficult to transition to other engines (such as Cesium for 3D globe visualization or Leaflet for mobile simplicity).

## Decision
We enforce a unified **Renderer Registry Interface**.
*   Core frontend features interact exclusively with a generic `MapRenderer` abstraction type.
*   Concrete rendering adapters (MapLibre, Cesium, Leaflet) must implement this interface and register with the Renderer Registry.
*   We define a structured `RendererCapabilities` descriptor model, allowing UI features to adapt based on capabilities (e.g. `supports3D`, `supportsOffline`) rather than hardcoded map engine classes.

## Consequences
*   *Pros*: Makes WebGIS engines fully swappable; isolates viewport lifecycle hooks.
*   *Cons*: Writing complete renderer adapters increases initialization code complexity.
