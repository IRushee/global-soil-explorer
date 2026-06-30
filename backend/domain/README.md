# Domain Module

## Purpose
Define the core soil science models and business validation rules.

## Responsibilities
*   Structure soil physical, chemical, and spatial entities.
*   Enforce domain invariants (e.g. property ranges, stacking logic).

## Allowed Contents
*   Domain entity classes (e.g., SoilProfile, SoilLayer, SoilComponent)
*   Domain validation rules
*   Unit conversion helpers
*   Profile vertical stacking order checks

## Forbidden Contents
*   Web server framework dependencies
*   Database drivers or engines
*   SQL query strings
*   File path configuration loaders
