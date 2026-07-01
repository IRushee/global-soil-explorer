# ADR-006: Application Service is Orchestration Only

## Status
Accepted

## Context
As applications grow, the application service layer often accumulates business logic, SQL queries, raster math, or HTTP/API formatting details. This results in bloated service classes that violate the Single Responsibility Principle, are difficult to maintain, and mix policy (business rules) with detail (infrastructure).

## Decision
The Application Service acts strictly as a thin coordination layer.
*   **Responsibilities**: It is only responsible for checking coordinate boundary values, invoking the spatial lookup service to resolve coordinate to SMU ID, querying the repository to get the soil observation, and mapping exceptions.
*   **Strict Prohibitions**: It must not execute database queries (no SQL), perform raster calculations, construct or modify scientific definitions, parse JSON, format HTTP response codes, or depend on FastAPI.

## Consequences
*   **Separation of Concerns**: The application layer acts as a clean bridge between API endpoints and core domain/repository logic.
*   **No Business Logic Accumulation**: Business rules remain in the Domain layer, while infrastructure logic remains in Repository/Spatial adapters.
*   **Maintainable and Testable**: The service depends only on abstraction interfaces, making it easy to test using simple mocks.
