# ruff: noqa
"""API Performance Benchmark.
Measures E2E latency, Application Service latency, and Serialization latency.
"""

import sqlite3
import statistics
import sys
import threading
import time
from pathlib import Path
from fastapi.testclient import TestClient

# Setup paths relative to the project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BIL_PATH = PROJECT_ROOT / "data" / "raw" / "hwsd" / "HWSD2.bil"
DEFAULT_HDR_PATH = PROJECT_ROOT / "data" / "raw" / "hwsd" / "HWSD2.hdr"
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "output" / "hwsd.db"

from backend.api.app import app
from backend.domain import Coordinate

# Connection caching proxy
thread_local = threading.local()
original_connect = sqlite3.connect


class ConnectionWrapper:

    def __init__(self, conn):
        self._conn = conn

    def cursor(self, *args, **kwargs):
        return self._conn.cursor(*args, **kwargs)

    def close(self):
        pass

    def __getattr__(self, name):
        return getattr(self._conn, name)


def cached_connect(database, *args, **kwargs):
    if not hasattr(thread_local, "connections"):
        thread_local.connections = {}
    if database not in thread_local.connections:
        conn = original_connect(database, *args, **kwargs)
        thread_local.connections[database] = conn
    return ConnectionWrapper(thread_local.connections[database])


def main():
    print("=== STARTING API PERFORMANCE BENCHMARK ===")

    # Enable SQLite caching to make 10,000 requests fast and avoid disk I/O bottlenecks
    sqlite3.connect = cached_connect

    LATITUDE = 52.0
    LONGITUDE = 10.0
    coord = Coordinate(LATITUDE, LONGITUDE)

    with TestClient(app) as client:
        spatial_lookup = app.state.spatial_lookup
        repository = app.state.repository
        app_service = app.state.application_service

        # Warmup
        for _ in range(10):
            client.get(
                "/soil", params={"latitude": LATITUDE, "longitude": LONGITUDE}
            )

        for count in [1, 100, 1000, 10000]:
            print(f"\nBenchmarking {count} requests...")

            api_times = []
            app_times = []
            serialization_times = []

            for _ in range(count):
                # 1. API E2E
                t0 = time.perf_counter()
                client.get(
                    "/soil",
                    params={"latitude": LATITUDE, "longitude": LONGITUDE},
                )
                t1 = time.perf_counter()
                api_times.append((t1 - t0) * 1000.0)

                # 2. Application Service
                t0 = time.perf_counter()
                obs = app_service.get_soil_observation(coord)
                t1 = time.perf_counter()
                app_times.append((t1 - t0) * 1000.0)

                # 3. Serialization
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

                t0 = time.perf_counter()
                if obs:
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
                    schema.model_dump_json()
                t2 = time.perf_counter()
                serialization_times.append((t2 - t0) * 1000.0)

            avg_api = statistics.mean(api_times)
            avg_app = statistics.mean(app_times)
            avg_ser = statistics.mean(serialization_times)
            avg_overhead = max(0.0, avg_api - avg_app - avg_ser)

            median_api = statistics.median(api_times)
            p95_api = (
                statistics.quantiles(api_times, n=20)[18]
                if count >= 20
                else api_times[-1]
            )
            p99_api = (
                statistics.quantiles(api_times, n=100)[98]
                if count >= 100
                else api_times[-1]
            )

            print(f"Results for {count} requests:")
            print(f"  Total API Latency (Avg):   {avg_api:.3f} ms")
            print(f"  Total API Latency (Median): {median_api:.3f} ms")
            print(f"  Total API Latency (P95):    {p95_api:.3f} ms")
            print(f"  Total API Latency (P99):    {p99_api:.3f} ms")
            print(f"  Breakdown:")
            print(f"    - Application Service:   {avg_app:.3f} ms")
            print(f"    - Serialization (Pydantic+JSON): {avg_ser:.3f} ms")
            print(
                f"    - FastAPI / TestClient Overhead: {avg_overhead:.3f} ms"
            )

    # Cleanup connection cache
    sqlite3.connect = original_connect
    if hasattr(thread_local, "connections"):
        for conn in thread_local.connections.values():
            try:
                conn.close()
            except Exception:
                pass
        thread_local.connections.clear()


if __name__ == "__main__":
    main()
