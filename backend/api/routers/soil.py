"""Soil observation query API endpoint routing."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from backend.api.dependencies import get_application_service, get_repository, get_spatial_lookup
from backend.api.schemas.response import (
    ChemicalPropertiesSchema,
    CoordinateSchema,
    DatasetMetadataCodes,
    DatasetMetadataSchema,
    EnvironmentalContextSchema,
    ErrorResponseSchema,
    HydraulicPropertiesSchema,
    HydrologicContextCodes,
    HydrologicContextSchema,
    LandLimitationsCodes,
    LandLimitationsSchema,
    LayerMeasurementsSchema,
    PhysicalPropertiesSchema,
    SoilClassificationCodes,
    SoilClassificationSchema,
    SoilLayerSchema,
    SoilObservationSchema,
    SoilProfileSchema,
    SoilPropertySchema,
    SoilTextureCodes,
    SoilTextureSchema,
)
from typing import Any
from backend.contracts.spatial_lookup import SpatialLookupService
from backend.application.exceptions import ApplicationServiceError
from backend.application.service import ApplicationService
from backend.repository.sqlite_repository import SQLiteSoilObservationRepository
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
    spatial_lookup: SpatialLookupService[Any] = Depends(get_spatial_lookup),
    repository: SQLiteSoilObservationRepository = Depends(get_repository),
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

    # Resolve metadata & environmental context from repo
    smu_id = spatial_lookup.resolve(coord)
    try:
        repo_obs = repository.get_by_key(smu_id, coordinate=coord) if smu_id is not None else None
    except Exception:
        repo_obs = None

    # 4. Serialize domains into explicit public Pydantic output schemas
    return SoilObservationSchema(
        coordinate=CoordinateSchema(
            latitude=observation.coordinate.latitude,
            longitude=observation.coordinate.longitude,
        ),
        environmental_context=EnvironmentalContextSchema(
            koppen_climate=repo_obs.environmental_context.koppen_climate
        ) if repo_obs and repo_obs.environmental_context else None,
        metadata=DatasetMetadataSchema(
            coverage_description=repository._coverage_lookup.get(str(repo_obs.metadata.coverage).upper())
            if repo_obs and repo_obs.metadata and repo_obs.metadata.coverage is not None
            else None,
            library=repo_obs.metadata.library if repo_obs and repo_obs.metadata else None,
            source=repo_obs.metadata.source if repo_obs and repo_obs.metadata else None,
            dataset_version=repo_obs.metadata.dataset_version if repo_obs and repo_obs.metadata else None,
            reference_identifiers=[
                ["SMU_ID", p[1]] if p[0] == "HWSD2_SMU_ID" else [p[0], p[1]]
                for p in repo_obs.metadata.reference_identifiers
            ]
            if repo_obs and repo_obs.metadata and repo_obs.metadata.reference_identifiers
            else None,
            codes=DatasetMetadataCodes(
                coverage=repo_obs.metadata.coverage if repo_obs and repo_obs.metadata else None
            ),
        ) if repo_obs and repo_obs.metadata else None,
        profiles=[
            SoilProfileSchema(
                composition_share=profile.composition_share,
                sequence_index=profile.sequence_index,
                classification=SoilClassificationSchema(
                    taxonomy_standard=profile.classification.taxonomy_standard,
                    class_name=profile.classification.class_name,
                    wrb4_name=profile.classification.wrb4_name,
                    wrb2_name=profile.classification.wrb2_name,
                    fao90_name=profile.classification.fao90_name,
                    wrb_phase_name=profile.classification.wrb_phase_name,
                    national_classification=profile.classification.national_classification,
                    codes=SoilClassificationCodes(
                        class_symbol=profile.classification.class_symbol,
                        wrb4_code=profile.classification.wrb4_code,
                        wrb2_code=profile.classification.wrb2_code,
                        fao90_code=profile.classification.fao90_code,
                        wrb_phase_code=profile.classification.wrb_phase_code,
                        dominant_group_code=profile.classification.dominant_group_code,
                    ),
                ),
                hydrologic_context=HydrologicContextSchema(
                    drainage_description=repository._drainage_lookup.get(str(profile.hydrologic_context.drainage).upper())
                    if profile.hydrologic_context and profile.hydrologic_context.drainage is not None
                    else None,
                    water_regime_description=repository._swr_lookup.get(str(profile.hydrologic_context.water_regime).upper())
                    if profile.hydrologic_context and profile.hydrologic_context.water_regime is not None
                    else None,
                    impermeable_layer_description=repository._il_lookup.get(str(profile.hydrologic_context.impermeable_layer).upper())
                    if profile.hydrologic_context and profile.hydrologic_context.impermeable_layer is not None
                    else None,
                    codes=HydrologicContextCodes(
                        drainage=profile.hydrologic_context.drainage,
                        water_regime=profile.hydrologic_context.water_regime,
                        impermeable_layer=profile.hydrologic_context.impermeable_layer,
                    ),
                ) if profile.hydrologic_context else None,
                land_limitations=LandLimitationsSchema(
                    root_depth_description=repository._root_depth_lookup.get(str(profile.land_limitations.root_depth).upper())
                    if profile.land_limitations and profile.land_limitations.root_depth is not None
                    else None,
                    root_obstacles_description=repository._roots_lookup.get(str(profile.land_limitations.root_obstacles).upper())
                    if profile.land_limitations and profile.land_limitations.root_obstacles is not None
                    else None,
                    phase1_description=repository._phase_lookup.get(str(profile.land_limitations.phase1).upper())
                    if profile.land_limitations and profile.land_limitations.phase1 is not None
                    else None,
                    phase2_description=repository._phase_lookup.get(str(profile.land_limitations.phase2).upper())
                    if profile.land_limitations and profile.land_limitations.phase2 is not None
                    else None,
                    additional_property_description=repository._add_prop_lookup.get(str(profile.land_limitations.additional_property).upper())
                    if profile.land_limitations and profile.land_limitations.additional_property is not None
                    else None,
                    codes=LandLimitationsCodes(
                        root_depth=profile.land_limitations.root_depth,
                        root_obstacles=profile.land_limitations.root_obstacles,
                        phase1=profile.land_limitations.phase1,
                        phase2=profile.land_limitations.phase2,
                        additional_property=profile.land_limitations.additional_property,
                    ),
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
                            usda_texture_description=repository._usda_texture_lookup.get(str(layer.texture.usda_texture).upper())
                            if layer.texture and layer.texture.usda_texture is not None
                            else None,
                            soter_texture_description=repository._soter_texture_lookup.get(str(layer.texture.soter_texture).upper())
                            if layer.texture and layer.texture.soter_texture is not None
                            else None,
                            codes=SoilTextureCodes(
                                usda_texture=layer.texture.usda_texture,
                                soter_texture=layer.texture.soter_texture,
                            ),
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
