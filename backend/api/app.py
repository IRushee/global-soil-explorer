"""Main FastAPI Application entrypoint and lifecycle configuration."""

import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from backend.api.exceptions import register_exception_handlers
from backend.api.routers import health, soil
from backend.application.service import ApplicationService
from backend.repository.sqlite_repository import SQLiteSoilObservationRepository
from backend.spatial.raster_lookup import BILRasterSpatialLookupService

# Resolve standard repository and dataset paths relative to project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_BIL_PATH = PROJECT_ROOT / "data" / "raw" / "hwsd" / "HWSD2.bil"
DEFAULT_HDR_PATH = PROJECT_ROOT / "data" / "raw" / "hwsd" / "HWSD2.hdr"
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "output" / "hwsd.db"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application-level service lifecycles (startup & cleanup)."""
    # 1. Resolve paths with potential env overrides
    bil_path = Path(os.getenv("HWSD_BIL_PATH", DEFAULT_BIL_PATH))
    hdr_path = Path(os.getenv("HWSD_HDR_PATH", DEFAULT_HDR_PATH))
    db_path = Path(os.getenv("HWSD_DB_PATH", DEFAULT_DB_PATH))

    # 2. Instantiate core services exactly once
    spatial_lookup = BILRasterSpatialLookupService(bil_path, hdr_path)
    repository = SQLiteSoilObservationRepository(db_path)
    app_service = ApplicationService(spatial_lookup, repository)

    # 3. Expose to app state for dynamic injection
    app.state.spatial_lookup = spatial_lookup
    app.state.repository = repository
    app.state.application_service = app_service

    yield

    # 4. Cleanup/close files on shutdown
    try:
        spatial_lookup.close()
    except Exception:
        pass


def create_app() -> FastAPI:
    """Construct and configure the FastAPI application instance."""
    app = FastAPI(
        title="Global Soil Explorer API",
        description=(
            "REST API exposing Harmonized World Soil Database (HWSD) v2.0 "
            "dataset spatial lookup and database queries."
        ),
        version="0.1.0",
        lifespan=lifespan,
    )

    # Register custom and override exception handlers
    register_exception_handlers(app)

    # Mount API routers under version prefix
    app.include_router(health.router, prefix="/v1")
    app.include_router(soil.router, prefix="/v1")

    # Mount unversioned API routers for backward compatibility aliases
    app.include_router(health.router)
    app.include_router(soil.router)

    return app


app = create_app()
