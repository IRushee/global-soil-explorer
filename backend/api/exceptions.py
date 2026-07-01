"""API exception handlers to convert service and validation errors to HTTP responses."""

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from backend.application.exceptions import ApplicationServiceError
from backend.domain.exceptions import InvalidCoordinateError


async def invalid_coordinate_handler(
    request: Request, exc: InvalidCoordinateError
) -> JSONResponse:
    """Handle domain-level InvalidCoordinateError by returning HTTP 400."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )


async def application_service_error_handler(
    request: Request, exc: ApplicationServiceError
) -> JSONResponse:
    """Handle infrastructure ApplicationServiceError by returning HTTP 503."""
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": str(exc)},
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Custom validator returning 400 for coordinate parsing errors."""
    if "/soil" in str(request.url):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "detail": (
                    "Invalid coordinate query parameters. Latitude and "
                    "longitude must be valid floating point numbers."
                )
            },
        )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register custom exception handlers with the FastAPI application."""
    app.add_exception_handler(
        InvalidCoordinateError,
        invalid_coordinate_handler,  # type: ignore[arg-type]
    )
    app.add_exception_handler(
        ApplicationServiceError,
        application_service_error_handler,  # type: ignore[arg-type]
    )
    app.add_exception_handler(
        RequestValidationError,
        validation_exception_handler,  # type: ignore[arg-type]
    )
