# ruff: noqa
"""API Response Serialization Benchmark.
Measures Pydantic schema mapping and JSON serialization latencies on large observations.
"""

import json
import statistics
import sys
import time
from pathlib import Path

# Setup paths relative to the project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BIL_PATH = PROJECT_ROOT / "data" / "raw" / "hwsd" / "HWSD2.bil"
DEFAULT_HDR_PATH = PROJECT_ROOT / "data" / "raw" / "hwsd" / "HWSD2.hdr"
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "output" / "hwsd.db"

from backend.application.service import ApplicationService
from backend.domain import Coordinate
from backend.repository.sqlite_repository import SQLiteSoilObservationRepository
from backend.spatial.raster_lookup import BILRasterSpatialLookupService


def main():
    print("=== STARTING SERIALIZATION AND API PERFORMANCE AUDIT ===")

    # Initialize
    spatial_lookup = BILRasterSpatialLookupService(
        DEFAULT_BIL_PATH, DEFAULT_HDR_PATH
    )
    repository = SQLiteSoilObservationRepository(DEFAULT_DB_PATH)
    app_service = ApplicationService(spatial_lookup, repository)

    # Target Coordinate - Germany (land pixel with multiple profiles and layers)
    coord = Coordinate(52.0, 10.0)

    # Retrieve observation
    obs = app_service.get_soil_observation(coord)
    if obs is None:
        print("Error: Could not retrieve soil observation for coordinate.")
        sys.exit(1)

    print(
        f"Observation retrieved: Coordinate ({coord.latitude}, {coord.longitude})"
    )
    print(f"Number of Profiles: {len(obs.profiles)}")
    for i, profile in enumerate(obs.profiles):
        print(
            f"  - Profile {i+1} Class: {profile.classification.class_name} ({profile.classification.class_symbol})"
        )
        print(f"  - Profile {i+1} Layers Count: {len(profile.layers)}")

    # Import Pydantic response models
    print("\nMeasuring serialization latency...")
    from backend.api.schemas.response import (
        ChemicalPropertiesSchema,
        CoordinateSchema,
        DatasetMetadataSchema,
        EnvironmentalContextSchema,
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

    # We will measure mapping + serialization 10,000 times
    t_start = time.perf_counter()
    for _ in range(10000):
        # Perform mapping to schema
        schema = SoilObservationSchema(
            coordinate=CoordinateSchema(
                latitude=obs.coordinate.latitude,
                longitude=obs.coordinate.longitude,
            ),
            environmental_context=EnvironmentalContextSchema(
                koppen_climate=obs.environmental_context.koppen_climate
            )
            if obs.environmental_context
            else None,
            metadata=DatasetMetadataSchema(
                coverage=obs.metadata.coverage,
                library=obs.metadata.library,
                source=obs.metadata.source,
                dataset_version=obs.metadata.dataset_version,
                reference_identifiers=[
                    [p[0], p[1]]
                    for p in obs.metadata.reference_identifiers
                ]
                if obs.metadata.reference_identifiers
                else None,
            )
            if obs.metadata
            else None,
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
                    )
                    if profile.hydrologic_context
                    else None,
                    land_limitations=LandLimitationsSchema(
                        root_depth=profile.land_limitations.root_depth,
                        root_obstacles=profile.land_limitations.root_obstacles,
                        phase1=profile.land_limitations.phase1,
                        phase2=profile.land_limitations.phase2,
                        additional_property=profile.land_limitations.additional_property,
                    )
                    if profile.land_limitations
                    else None,
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
                            )
                            if layer.texture
                            else None,
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
                            )
                            if layer.measurements
                            else None,
                        )
                        for layer in profile.layers
                    ],
                )
                for profile in obs.profiles
            ],
        )

        # Serialize to JSON string
        json_data = schema.model_dump_json()

    t_end = time.perf_counter()

    total_time_ms = (t_end - t_start) * 1000.0
    avg_serialization_time_ms = total_time_ms / 10000.0

    print(f"Serialization Benchmark (10,000 iterations):")
    print(f"  - Total Time: {total_time_ms:.2f} ms")
    print(
        f"  - Avg serialization time: {avg_serialization_time_ms:.3f} ms per observation"
    )

    # Payload size
    json_bytes = len(json_data.encode("utf-8"))
    print(
        f"  - Response JSON payload size: {json_bytes} bytes ({json_bytes/1024.0:.3f} KB)"
    )

    spatial_lookup.close()


if __name__ == "__main__":
    main()
