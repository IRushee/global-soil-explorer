"""Soil observation query API endpoint routing."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from backend.api.dependencies import get_application_service
from backend.api.schemas.response import (
    ChemicalPropertiesSchema,
    CoordinateSchema,
    DatasetMetadataSchema,
    EnvironmentalContextSchema,
    ErrorResponseSchema,
    HydraulicPropertiesSchema,
    HydrologicContextSchema,
    LandLimitationsSchema,
    LayerMeasurementsSchema,
    PhysicalPropertiesSchema,
    SoilClassificationSchema,
    SoilLayerSchema,
    SoilObservationSchema,
    SoilProfileSchema,
    SoilPropertySchema,
    SoilTextureSchema,
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
        environmental_context=EnvironmentalContextSchema(
            koppen_climate=observation.environmental_context.koppen_climate
        ) if observation.environmental_context else None,
        metadata=DatasetMetadataSchema(
            coverage=observation.metadata.coverage,
            library=observation.metadata.library,
            source=observation.metadata.source,
            dataset_version=observation.metadata.dataset_version,
            reference_identifiers=[
                [p[0], p[1]]
                for p in observation.metadata.reference_identifiers
            ]
            if observation.metadata.reference_identifiers
            else None,
        ) if observation.metadata else None,
        profiles=[
            SoilProfileSchema(
                composition_share=profile.composition_share,
                sequence_index=profile.sequence_index,
                classification=SoilClassificationSchema(
                    taxonomy_standard=profile.classification.taxonomy_standard,
                    class_symbol=profile.classification.class_symbol,
                    class_name=profile.classification.class_name,
                    wrb4_code=profile.classification.wrb4_code,
                    wrb4_name=profile.classification.wrb4_name,
                    wrb2_code=profile.classification.wrb2_code,
                    wrb2_name=profile.classification.wrb2_name,
                    fao90_code=profile.classification.fao90_code,
                    fao90_name=profile.classification.fao90_name,
                    wrb_phase_code=profile.classification.wrb_phase_code,
                    wrb_phase_name=profile.classification.wrb_phase_name,
                    dominant_group_code=profile.classification.dominant_group_code,
                    national_classification=profile.classification.national_classification,
                ),
                hydrologic_context=HydrologicContextSchema(
                    drainage=profile.hydrologic_context.drainage,
                    water_regime=profile.hydrologic_context.water_regime,
                    impermeable_layer=profile.hydrologic_context.impermeable_layer,
                ) if profile.hydrologic_context else None,
                land_limitations=LandLimitationsSchema(
                    root_depth=profile.land_limitations.root_depth,
                    root_obstacles=profile.land_limitations.root_obstacles,
                    phase1=profile.land_limitations.phase1,
                    phase2=profile.land_limitations.phase2,
                    additional_property=profile.land_limitations.additional_property,
                ) if profile.land_limitations else None,
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
                        texture=SoilTextureSchema(
                            usda_texture=layer.texture.usda_texture,
                            soter_texture=layer.texture.soter_texture,
                        ) if layer.texture else None,
                        measurements=LayerMeasurementsSchema(
                            physical=PhysicalPropertiesSchema(
                                sand=layer.measurements.physical.sand,
                                silt=layer.measurements.physical.silt,
                                clay=layer.measurements.physical.clay,
                                coarse_fragments=layer.measurements.physical.coarse_fragments,
                                bulk_density=layer.measurements.physical.bulk_density,
                                ref_bulk_density=layer.measurements.physical.ref_bulk_density,
                            ),
                            chemical=ChemicalPropertiesSchema(
                                ph=layer.measurements.chemical.ph,
                                organic_carbon=layer.measurements.chemical.organic_carbon,
                                total_nitrogen=layer.measurements.chemical.total_nitrogen,
                                cn_ratio=layer.measurements.chemical.cn_ratio,
                                cec_soil=layer.measurements.chemical.cec_soil,
                                cec_clay=layer.measurements.chemical.cec_clay,
                                effective_cec=layer.measurements.chemical.effective_cec,
                                teb=layer.measurements.chemical.teb,
                                base_saturation=layer.measurements.chemical.base_saturation,
                                aluminum_saturation=layer.measurements.chemical.aluminum_saturation,
                                esp=layer.measurements.chemical.esp,
                                calcium_carbonate=layer.measurements.chemical.calcium_carbonate,
                                gypsum=layer.measurements.chemical.gypsum,
                                electrical_conductivity=layer.measurements.chemical.electrical_conductivity,
                            ),
                            hydraulic=HydraulicPropertiesSchema(
                                available_water_capacity=layer.measurements.hydraulic.available_water_capacity,
                            ),
                        ) if layer.measurements else None,
                    )
                    for layer in profile.layers
                ],
            )
            for profile in observation.profiles
        ],
    )
