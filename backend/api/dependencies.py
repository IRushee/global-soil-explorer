from typing import Any, cast

from fastapi import Request

from backend.application.service import ApplicationService
from backend.contracts.repository import SoilObservationRepository
from backend.contracts.spatial_lookup import SpatialLookupService


def get_spatial_lookup(request: Request) -> SpatialLookupService[Any]:
    """Inject the spatial lookup service."""
    return cast(SpatialLookupService[Any], request.app.state.spatial_lookup)


def get_repository(request: Request) -> SoilObservationRepository[Any]:
    """Inject the soil observation repository."""
    return cast(SoilObservationRepository[Any], request.app.state.repository)


def get_application_service(request: Request) -> ApplicationService:
    """Inject the coordinate query application service."""
    return cast(ApplicationService, request.app.state.application_service)
