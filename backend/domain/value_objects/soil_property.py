"""SoilProperty value object representing chemical and physical attributes."""

import math
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Final

from backend.domain.constants import (
    MAX_PERCENTAGE,
    MAX_PH,
    MIN_AVAILABLE_WATER_CAPACITY,
    MIN_CATION_EXCHANGE_CAPACITY,
    MIN_DEPTH_LIMIT,
    MIN_ORGANIC_CARBON,
    MIN_PERCENTAGE,
    MIN_PH,
)
from backend.domain.exceptions import InvalidPropertyError


class PropertyType(StrEnum):
    """Supported standard physical and chemical soil properties."""

    PH_WATER = "ph_water"
    BULK_DENSITY = "bulk_density"
    COARSE_FRAGMENTS = "coarse_fragments"
    ROOTING_DEPTH_LIMIT = "rooting_depth_limit"
    CATION_EXCHANGE_CAPACITY = "cation_exchange_capacity"
    BASE_SATURATION = "base_saturation"
    AVAILABLE_WATER_CAPACITY = "available_water_capacity"
    ORGANIC_CARBON = "organic_carbon"
    SAND = "sand"
    SILT = "silt"
    CLAY = "clay"


class Unit(StrEnum):
    """Standardized scientific units of measure."""

    PERCENT = "percent"
    GRAM_PER_CUBIC_CENTIMETER = "g_cm3"
    CENTIMOL_CHARGE_PER_KG = "cmolc_kg"
    MILLIMETER = "mm"
    CENTIMETER = "cm"
    PH = "ph"


@dataclass(frozen=True, slots=True)
class PropertyDefinition:
    """Defines type restrictions and validation invariants for a soil property."""

    canonical_unit: Unit
    min_value: float | None = None
    max_value: float | None = None
    is_strictly_positive: bool = False

    def validate(self, value: float, unit: Unit, property_type: PropertyType) -> None:
        """Enforce unit consistency and range bounds with informative messages."""
        if unit != self.canonical_unit:
            raise InvalidPropertyError(
                f"Invalid unit for property '{property_type.value}'. "
                f"Expected '{self.canonical_unit.value}', got '{unit.value}'."
            )
        if self.is_strictly_positive and value <= 0.0:
            raise InvalidPropertyError(
                f"Value for property '{property_type.value}' must be strictly positive."
            )
        if self.min_value is not None and value < self.min_value:
            raise InvalidPropertyError(
                f"Value for property '{property_type.value}' "
                f"cannot be less than {self.min_value}."
            )
        if self.max_value is not None and value > self.max_value:
            raise InvalidPropertyError(
                f"Value for property '{property_type.value}' "
                f"cannot be greater than {self.max_value}."
            )


_DEFINITIONS_MAP = {
    PropertyType.PH_WATER: PropertyDefinition(
        canonical_unit=Unit.PH, min_value=MIN_PH, max_value=MAX_PH
    ),
    PropertyType.SAND: PropertyDefinition(
        canonical_unit=Unit.PERCENT, min_value=MIN_PERCENTAGE, max_value=MAX_PERCENTAGE
    ),
    PropertyType.SILT: PropertyDefinition(
        canonical_unit=Unit.PERCENT, min_value=MIN_PERCENTAGE, max_value=MAX_PERCENTAGE
    ),
    PropertyType.CLAY: PropertyDefinition(
        canonical_unit=Unit.PERCENT, min_value=MIN_PERCENTAGE, max_value=MAX_PERCENTAGE
    ),
    PropertyType.BASE_SATURATION: PropertyDefinition(
        canonical_unit=Unit.PERCENT, min_value=MIN_PERCENTAGE, max_value=MAX_PERCENTAGE
    ),
    PropertyType.COARSE_FRAGMENTS: PropertyDefinition(
        canonical_unit=Unit.PERCENT, min_value=MIN_PERCENTAGE, max_value=MAX_PERCENTAGE
    ),
    PropertyType.BULK_DENSITY: PropertyDefinition(
        canonical_unit=Unit.GRAM_PER_CUBIC_CENTIMETER, is_strictly_positive=True
    ),
    PropertyType.ORGANIC_CARBON: PropertyDefinition(
        canonical_unit=Unit.PERCENT, min_value=MIN_ORGANIC_CARBON
    ),
    PropertyType.ROOTING_DEPTH_LIMIT: PropertyDefinition(
        canonical_unit=Unit.CENTIMETER, min_value=MIN_DEPTH_LIMIT
    ),
    PropertyType.CATION_EXCHANGE_CAPACITY: PropertyDefinition(
        canonical_unit=Unit.CENTIMOL_CHARGE_PER_KG,
        min_value=MIN_CATION_EXCHANGE_CAPACITY,
    ),
    PropertyType.AVAILABLE_WATER_CAPACITY: PropertyDefinition(
        canonical_unit=Unit.MILLIMETER, min_value=MIN_AVAILABLE_WATER_CAPACITY
    ),
}

PROPERTY_DEFINITIONS: Final[MappingProxyType[PropertyType, PropertyDefinition]] = (
    MappingProxyType(_DEFINITIONS_MAP)
)


@dataclass(frozen=True, slots=True)
class SoilProperty:
    """Represents a validated, immutable physical or chemical soil attribute."""

    property_type: PropertyType
    value: float
    unit: Unit

    def __post_init__(self) -> None:
        """Validate type, finite values, and range definition policies."""
        # 1. Type validation
        if not isinstance(self.property_type, PropertyType):
            raise InvalidPropertyError("property_type must be a PropertyType enum.")
        if not isinstance(self.unit, Unit):
            raise InvalidPropertyError("unit must be a Unit enum.")
        if not isinstance(self.value, (int, float)) or isinstance(self.value, bool):
            raise InvalidPropertyError("value must be a numeric float or integer.")

        # 2. Force float conversion
        object.__setattr__(self, "value", float(self.value))

        # 3. Reject non-finite values (NaN / Inf)
        if not math.isfinite(self.value):
            raise InvalidPropertyError("value must be a finite number.")

        # 4. Invoke Policy Validation
        definition = PROPERTY_DEFINITIONS.get(self.property_type)
        if not definition:
            raise InvalidPropertyError(
                f"Missing property definition for type '{self.property_type.value}'."
            )
        definition.validate(self.value, self.unit, self.property_type)
