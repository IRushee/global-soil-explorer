"""Response serialization models for the Global Soil Explorer API."""

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


class SoilPropertySchema(BaseModel):
    """Measured chemical or physical soil property schema."""

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
    """Vertical soil layer schema."""

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
        description="Chemical and physical property values in this layer.",
    )


class SoilClassificationSchema(BaseModel):
    """Taxonomic soil classification schema."""

    taxonomy_standard: str = Field(
        ...,
        description="Classification system standard name.",
        json_schema_extra={"example": "WRB 2022"},
    )
    class_symbol: str = Field(
        ...,
        description="Taxonomic class identifier code.",
        json_schema_extra={"example": "LV"},
    )
    class_name: str = Field(
        ...,
        description="Human-readable soil class description.",
        json_schema_extra={"example": "Luvisols"},
    )


class SoilProfileSchema(BaseModel):
    """Soil profile schema."""

    layers: list[SoilLayerSchema] = Field(
        ..., description="Stack of vertical soil layers ordered by depth."
    )
    classification: SoilClassificationSchema = Field(
        ..., description="Taxonomic classification of the profile."
    )
    composition_share: float | None = Field(
        None,
        description="Percentage composition of this profile in the spatial unit.",
        json_schema_extra={"example": 80.0},
    )


class SoilObservationSchema(BaseModel):
    """Coordinated soil observation response schema."""

    coordinate: CoordinateSchema = Field(
        ..., description="The query coordinate associated with this observation."
    )
    profiles: list[SoilProfileSchema] = Field(
        ..., description="The list of soil profiles matching this spatial location."
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
