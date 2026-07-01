"""Response serialization schemas for the Global Soil Explorer API."""

from pydantic import BaseModel, Field

from backend.domain import PropertyType, Unit


class CoordinateSchema(BaseModel):
    """Geographic coordinate schema."""

    latitude: float = Field(
        ...,
        description="Latitude of the coordinate in decimal degrees.",
        json_schema_extra={"example": 52.0},
    )
    longitude: float = Field(
        ...,
        description="Longitude of the coordinate in decimal degrees.",
        json_schema_extra={"example": 10.0},
    )


class EnvironmentalContextSchema(BaseModel):
    """Climatic and environmental context of the soil site."""

    koppen_climate: str | None = Field(
        None,
        description="Koppen-Geiger climate classification code.",
        json_schema_extra={"example": "C"},
    )


class DatasetMetadataSchema(BaseModel):
    """Database source provenance and dataset metadata."""

    coverage: int | None = Field(
        None,
        description="Source map coverage identifier code.",
        json_schema_extra={"example": 1},
    )
    library: str | None = Field(
        None,
        description="WRB library identifier name.",
        json_schema_extra={"example": "HWSD"},
    )
    source: str | None = Field(
        None,
        description="Active database or data source description.",
        json_schema_extra={"example": "HWSD v2.0 Database"},
    )
    dataset_version: str | None = Field(
        None,
        description="Active dataset version indicator.",
        json_schema_extra={"example": "v2.0"},
    )
    reference_identifiers: list[list[str]] | None = Field(
        None,
        description="Identifiers referencing source records.",
        json_schema_extra={"example": [["HWSD2_SMU_ID", "10221"]]},
    )


class SoilClassificationSchema(BaseModel):
    """Taxonomic soil classification schema representing standard codes and values."""

    taxonomy_standard: str = Field(
        ...,
        description="Taxonomic classification standard.",
        json_schema_extra={"example": "WRB 2022"},
    )
    class_symbol: str = Field(
        ...,
        description="Taxonomic class identifier code.",
        json_schema_extra={"example": "LV"},
    )
    class_name: str = Field(
        ...,
        description="Taxonomic class description name.",
        json_schema_extra={"example": "Luvisols"},
    )
    wrb4_code: str | None = Field(
        None, description="WRB 4th Edition classification code."
    )
    wrb4_name: str | None = Field(
        None, description="WRB 4th Edition classification name."
    )
    wrb2_code: str | None = Field(
        None, description="WRB 2nd Edition classification code."
    )
    wrb2_name: str | None = Field(
        None, description="WRB 2nd Edition classification name."
    )
    fao90_code: str | None = Field(
        None, description="FAO 1990 classification code."
    )
    fao90_name: str | None = Field(
        None, description="FAO 1990 classification name."
    )
    wrb_phase_code: str | None = Field(
        None, description="WRB soil phase identifier code."
    )
    wrb_phase_name: str | None = Field(
        None, description="WRB soil phase name description."
    )
    dominant_group_code: str | None = Field(
        None, description="Dominant soil classification group code."
    )
    national_classification: str | None = Field(
        None, description="National soil classification system descriptor."
    )


class HydrologicContextSchema(BaseModel):
    """Hydrologic soil attributes schema."""

    drainage: str | None = Field(
        None,
        description="Natural soil drainage class code.",
        json_schema_extra={"example": "W"},
    )
    water_regime: int | None = Field(
        None,
        description="Water regime characteristics code.",
        json_schema_extra={"example": 1},
    )
    impermeable_layer: int | None = Field(
        None,
        description="Impermeable layer depth constraint class.",
        json_schema_extra={"example": 0},
    )


class LandLimitationsSchema(BaseModel):
    """Agronomic and physical growth limitations."""

    root_depth: int | None = Field(
        None,
        description="Total soil depth class accessible to plant roots.",
        json_schema_extra={"example": 1},
    )
    root_obstacles: int | None = Field(
        None,
        description="Mechanical obstacles class to plant roots.",
        json_schema_extra={"example": 0},
    )
    phase1: int | None = Field(
        None,
        description="Soil phase modifier limitation class 1.",
        json_schema_extra={"example": 0},
    )
    phase2: int | None = Field(
        None,
        description="Soil phase modifier limitation class 2.",
        json_schema_extra={"example": 0},
    )
    additional_property: int | None = Field(
        None,
        description="Additional soil property modifier constraints.",
        json_schema_extra={"example": 0},
    )


class SoilTextureSchema(BaseModel):
    """Soil layer texture schema."""

    usda_texture: int | None = Field(
        None,
        description="Soil texture class identifier based on USDA standard.",
        json_schema_extra={"example": 3},
    )
    soter_texture: str | None = Field(
        None,
        description="Soil texture class identifier based on SOTER standard.",
        json_schema_extra={"example": "M"},
    )


class PhysicalPropertiesSchema(BaseModel):
    """Soil physical measurements."""

    sand: float | None = Field(
        None,
        description="Weight share of sand fraction (%).",
        json_schema_extra={"example": 40.0},
    )
    silt: float | None = Field(
        None,
        description="Weight share of silt fraction (%).",
        json_schema_extra={"example": 30.0},
    )
    clay: float | None = Field(
        None,
        description="Weight share of clay fraction (%).",
        json_schema_extra={"example": 30.0},
    )
    coarse_fragments: float | None = Field(
        None,
        description="Volume share of coarse fragments (%).",
        json_schema_extra={"example": 5.0},
    )
    bulk_density: float | None = Field(
        None,
        description="Soil bulk density (g/cm³).",
        json_schema_extra={"example": 1.4},
    )
    ref_bulk_density: float | None = Field(
        None,
        description="Reference bulk density (g/cm³).",
        json_schema_extra={"example": 1.45},
    )


class ChemicalPropertiesSchema(BaseModel):
    """Soil chemical measurements."""

    ph: float | None = Field(
        None,
        description="Soil pH measured in water.",
        json_schema_extra={"example": 6.5},
    )
    organic_carbon: float | None = Field(
        None,
        description="Organic carbon share (%).",
        json_schema_extra={"example": 2.5},
    )
    total_nitrogen: float | None = Field(
        None,
        description="Total nitrogen concentration (g/kg).",
        json_schema_extra={"example": 0.15},
    )
    cn_ratio: float | None = Field(
        None,
        description="Carbon-to-Nitrogen ratio.",
        json_schema_extra={"example": 12.0},
    )
    cec_soil: float | None = Field(
        None,
        description="Cation Exchange Capacity of the soil (cmol(+)/kg).",
        json_schema_extra={"example": 15.0},
    )
    cec_clay: float | None = Field(
        None,
        description="Cation Exchange Capacity of the clay fraction (cmol(+)/kg).",
        json_schema_extra={"example": 24.0},
    )
    effective_cec: float | None = Field(
        None,
        description="Effective Cation Exchange Capacity (cmol(+)/kg).",
        json_schema_extra={"example": 14.8},
    )
    teb: float | None = Field(
        None,
        description="Total Exchangeable Bases (cmol(+)/kg).",
        json_schema_extra={"example": 10.0},
    )
    base_saturation: float | None = Field(
        None,
        description="Base Saturation index (%).",
        json_schema_extra={"example": 75.0},
    )
    aluminum_saturation: float | None = Field(
        None,
        description="Aluminum Saturation index (%).",
        json_schema_extra={"example": 0.0},
    )
    esp: float | None = Field(
        None,
        description="Exchangeable Sodium Percentage (%).",
        json_schema_extra={"example": 1.0},
    )
    calcium_carbonate: float | None = Field(
        None,
        description="Calcium carbonate equivalent (%).",
        json_schema_extra={"example": 2.0},
    )
    gypsum: float | None = Field(
        None,
        description="Gypsum weight share (%).",
        json_schema_extra={"example": 0.0},
    )
    electrical_conductivity: float | None = Field(
        None,
        description="Electrical conductivity (dS/m).",
        json_schema_extra={"example": 0.2},
    )


class HydraulicPropertiesSchema(BaseModel):
    """Soil hydraulic measurements."""

    available_water_capacity: float | None = Field(
        None,
        description="Available water capacity (mm).",
        json_schema_extra={"example": 150.0},
    )


class LayerMeasurementsSchema(BaseModel):
    """Consolidated layer measurement tables."""

    physical: PhysicalPropertiesSchema = Field(
        ..., description="Physical properties group."
    )
    chemical: ChemicalPropertiesSchema = Field(
        ..., description="Chemical properties group."
    )
    hydraulic: HydraulicPropertiesSchema = Field(
        ..., description="Hydraulic properties group."
    )


class SoilPropertySchema(BaseModel):
    """Legacy property model (retained for backward compatibility)."""

    property_type: PropertyType = Field(
        ...,
        description="The scientific property code/type.",
        json_schema_extra={"example": PropertyType.PH_WATER},
    )
    value: float = Field(
        ...,
        description="The numeric measurement value.",
        json_schema_extra={"example": 6.5},
    )
    unit: Unit = Field(
        ...,
        description="Standardized unit of measurement.",
        json_schema_extra={"example": Unit.PH},
    )


class SoilLayerSchema(BaseModel):
    """Vertical soil layer schema interval."""

    top_depth_cm: float = Field(
        ...,
        description="Depth to top of layer in centimeters.",
        json_schema_extra={"example": 0.0},
    )
    bottom_depth_cm: float = Field(
        ...,
        description="Depth to bottom of layer in centimeters.",
        json_schema_extra={"example": 30.0},
    )
    properties: list[SoilPropertySchema] = Field(
        ...,
        description="Chemical and physical property values list (backward compatible).",
    )
    texture: SoilTextureSchema | None = Field(
        None, description="Texture codes for this layer depth."
    )
    measurements: LayerMeasurementsSchema | None = Field(
        None, description="Consolidated chemical and physical measurement groups."
    )


class SoilProfileSchema(BaseModel):
    """Multi-layer vertical soil profile schema."""

    layers: list[SoilLayerSchema] = Field(
        ..., description="Stack of vertical soil layers ordered by depth."
    )
    classification: SoilClassificationSchema = Field(
        ..., description="Taxonomic classification details."
    )
    composition_share: float | None = Field(
        None,
        description="Percentage composition of this profile in the spatial unit.",
        json_schema_extra={"example": 80.0},
    )
    hydrologic_context: HydrologicContextSchema | None = Field(
        None, description="Hydrologic attributes of this profile."
    )
    land_limitations: LandLimitationsSchema | None = Field(
        None, description="Agronomic and growth limitation ratings."
    )
    sequence_index: int | None = Field(
        None,
        description="Rank of this profile in the overall mapping unit.",
        json_schema_extra={"example": 1},
    )


class SoilObservationSchema(BaseModel):
    """Scientific observation at location coordinates."""

    coordinate: CoordinateSchema = Field(
        ..., description="The query coordinate associated with this observation."
    )
    profiles: list[SoilProfileSchema] = Field(
        ..., description="The list of soil profiles matching this spatial location."
    )
    environmental_context: EnvironmentalContextSchema | None = Field(
        None, description="Environmental and climate descriptors of the site."
    )
    metadata: DatasetMetadataSchema | None = Field(
        None, description="Data provenance, standards, and dataset metadata."
    )


class HealthResponseSchema(BaseModel):
    """API and dataset health status schema."""

    status: str = Field(
        ...,
        description="Overall application health state (e.g. 'healthy').",
        json_schema_extra={"example": "healthy"},
    )
    runtime_version: str = Field(
        ...,
        description="Python runtime environment version.",
        json_schema_extra={"example": "3.11.15"},
    )
    dataset_name: str = Field(
        ...,
        description="Standardized name of the active dataset.",
        json_schema_extra={"example": "HWSD v2.0"},
    )
    dataset_version: str = Field(
        ...,
        description="Active dataset version identifier.",
        json_schema_extra={"example": "2.0"},
    )
    spatial_lookup_available: bool = Field(
        ..., description="Status of the spatial raster binary lookup service."
    )
    repository_available: bool = Field(
        ..., description="Status of the soil observation SQLite repository."
    )
    database_available: bool = Field(
        ..., description="Status of connection to the underlying database file."
    )


class ErrorResponseSchema(BaseModel):
    """Standardized API error message response."""

    detail: str = Field(
        ...,
        description="Detailed explanation of the error.",
        json_schema_extra={"example": "Latitude must be a numeric value."},
    )
