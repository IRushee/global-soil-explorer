"""Soil observation query API endpoint routing."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from backend.api.dependencies import get_application_service
from backend.api.schemas.response import (
    CoordinateSchema,
    ErrorResponseSchema,
    SoilClassificationSchema,
    SoilLayerSchema,
    SoilObservationSchema,
    SoilProfileSchema,
    SoilPropertySchema,
)
from backend.application.exceptions import ApplicationServiceError
from backend.application.service import ApplicationService
from backend.domain import Coordinate
from backend.domain.exceptions import InvalidCoordinateError

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/soil",
    response_model=SoilObservationSchema,
    responses={
        200: {
            "model": SoilObservationSchema,
            "description": "Coordinates resolved and observation returned.",
        },
        204: {
            "description": (
                "Coordinates resolved to a void/ocean area (no observation)."
            )
        },
        400: {
            "model": ErrorResponseSchema,
            "description": "Geographic coordinates are invalid or out of bounds.",
        },
        503: {
            "model": ErrorResponseSchema,
            "description": "Underlying spatial index or database unavailable.",
        },
        500: {
            "model": ErrorResponseSchema,
            "description": "Unexpected application failure.",
        },
    },
    summary="Query Soil Observation",
    description=(
        "Retrieves vertical soil profile properties, texture shares, and taxonomic "
        "classifications at the specified latitude and longitude coordinates."
    ),
)
def get_soil(
    latitude: float = Query(
        ...,
        description="Geographic latitude coordinate in decimal degrees (-90 to 90).",
        json_schema_extra={"example": 52.0},
    ),
    longitude: float = Query(
        ...,
        description="Geographic longitude coordinate in decimal degrees (-180 to 180).",
        json_schema_extra={"example": 10.0},
    ),
    app_service: ApplicationService = Depends(get_application_service),
) -> SoilObservationSchema | Response:
    """Coordinate query endpoint returning matching SoilObservation schemas."""
    # 1. Instantiate Coordinate - this triggers domain invariant validation
    try:
        coord = Coordinate(latitude=latitude, longitude=longitude)
    except InvalidCoordinateError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except (ValueError, TypeError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid parameter format: {e}",
        )

    # 2. Invoke application service to query the coordinates pipeline
    try:
        observation = app_service.get_soil_observation(coord)
    except InvalidCoordinateError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except ApplicationServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )
    except Exception:
        logger.exception("An unexpected error occurred during soil query processing.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected internal server error occurred.",
        )

    # 3. Handle coordinate lookup returning None (void/ocean pixel)
    if observation is None:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    # 4. Serialize domains into explicit public Pydantic output schemas
    return SoilObservationSchema(
        coordinate=CoordinateSchema(
            latitude=observation.coordinate.latitude,
            longitude=observation.coordinate.longitude,
        ),
        profiles=[
            SoilProfileSchema(
                composition_share=profile.composition_share,
                classification=SoilClassificationSchema(
                    taxonomy_standard=profile.classification.taxonomy_standard,
                    class_symbol=profile.classification.class_symbol,
                    class_name=profile.classification.class_name,
                ),
                layers=[
                    SoilLayerSchema(
                        top_depth_cm=layer.top_depth_cm,
                        bottom_depth_cm=layer.bottom_depth_cm,
                        properties=[
                            SoilPropertySchema(
                                property_type=prop.property_type,
                                value=prop.value,
                                unit=prop.unit,
                            )
                            for prop in layer.properties
                        ],
                    )
                    for layer in profile.layers
                ],
            )
            for profile in observation.profiles
        ],
    )
