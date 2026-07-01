"""Health routing endpoint monitoring backend runtime and database connectivity."""

import platform
import sqlite3
from typing import Any

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from backend.api.dependencies import get_repository, get_spatial_lookup
from backend.api.schemas.response import HealthResponseSchema
from backend.contracts.repository import SoilObservationRepository
from backend.contracts.spatial_lookup import SpatialLookupService

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponseSchema,
    responses={
        200: {
            "model": HealthResponseSchema,
            "description": "All infrastructure components are fully operational.",
        },
        503: {
            "model": HealthResponseSchema,
            "description": "One or more infrastructure components are unavailable.",
        },
    },
    summary="Check Application Health",
    description=(
        "Returns current health status and versions for python runtime, "
        "spatial lookup grid parser, and SQLite database connectivity."
    ),
)
def check_health(
    spatial_lookup: SpatialLookupService[Any] = Depends(get_spatial_lookup),
    repository: SoilObservationRepository[Any] = Depends(get_repository),
) -> HealthResponseSchema | JSONResponse:
    """Retrieve runtime status of lookup, database, and repository layers."""
    # 1. Check spatial lookup file handle state
    spatial_ok = False
    try:
        # Check if the service file handle exists and is open
        if hasattr(spatial_lookup, "_file") and not spatial_lookup._file.closed:
            spatial_ok = True
    except Exception:
        pass

    # 2. Check SQLite database file and basic connectivity
    db_ok = False
    try:
        if hasattr(repository, "_db_path") and repository._db_path.exists():
            # Open temporary connection to verify query parsing works
            conn = sqlite3.connect(str(repository._db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            conn.close()
            db_ok = True
    except Exception:
        pass

    # 3. Check repository mapping readiness
    repo_ok = False
    try:
        if hasattr(repository, "_wrb4_lookup") and isinstance(
            repository._wrb4_lookup, dict
        ):
            repo_ok = True
    except Exception:
        pass

    all_healthy = spatial_ok and db_ok and repo_ok
    status_str = "healthy" if all_healthy else "unhealthy"

    response_data = HealthResponseSchema(
        status=status_str,
        runtime_version=platform.python_version(),
        dataset_name="HWSD v2.0",
        dataset_version="2.0",
        spatial_lookup_available=spatial_ok,
        repository_available=repo_ok,
        database_available=db_ok,
    )

    if not all_healthy:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=response_data.model_dump(),
        )

    return response_data
