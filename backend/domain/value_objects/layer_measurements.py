"""LayerMeasurements value object grouping soil properties."""

import math
from dataclasses import dataclass

from backend.domain.constants import (
    MAX_PERCENTAGE,
    MAX_PH,
    MIN_PERCENTAGE,
    MIN_PH,
)
from backend.domain.exceptions import InvalidLayerMeasurementsError


def _check_float(val: float | int | None, name: str) -> float | None:
    """Validate and clean optional float parameters."""
    if val is None:
        return None
    if not isinstance(val, (int, float)) or isinstance(val, bool):
        raise InvalidLayerMeasurementsError(
            f"{name} must be a numeric float or integer."
        )
    f_val = float(val)
    if not math.isfinite(f_val):
        raise InvalidLayerMeasurementsError(f"{name} must be a finite number.")
    return f_val


def _validate_pct(val: float | int | None, name: str) -> float | None:
    """Enforce percentage bounds [0.0, 100.0]."""
    f_val = _check_float(val, name)
    if f_val is not None:
        if not (MIN_PERCENTAGE <= f_val <= MAX_PERCENTAGE):
            raise InvalidLayerMeasurementsError(
                f"{name} percentage must be between 0.0 and 100.0, got {f_val}."
            )
    return f_val


def _validate_non_negative(val: float | int | None, name: str) -> float | None:
    """Enforce non-negative boundary (>= 0.0)."""
    f_val = _check_float(val, name)
    if f_val is not None:
        if f_val < 0.0:
            raise InvalidLayerMeasurementsError(
                f"{name} must be non-negative, got {f_val}."
            )
    return f_val


def _validate_strictly_positive(val: float | int | None, name: str) -> float | None:
    """Enforce strictly positive boundary (> 0.0)."""
    f_val = _check_float(val, name)
    if f_val is not None:
        if f_val <= 0.0:
            raise InvalidLayerMeasurementsError(
                f"{name} must be strictly positive, got {f_val}."
            )
    return f_val


@dataclass(frozen=True, slots=True)
class PhysicalProperties:
    """Groups vertical layer physical measurements."""

    sand: float | None = None
    silt: float | None = None
    clay: float | None = None
    coarse_fragments: float | None = None
    bulk_density: float | None = None
    ref_bulk_density: float | None = None

    def __post_init__(self) -> None:
        """Validate physical soil properties."""
        object.__setattr__(self, "sand", _validate_pct(self.sand, "sand"))
        object.__setattr__(self, "silt", _validate_pct(self.silt, "silt"))
        object.__setattr__(self, "clay", _validate_pct(self.clay, "clay"))
        object.__setattr__(
            self,
            "coarse_fragments",
            _validate_pct(self.coarse_fragments, "coarse_fragments"),
        )
        object.__setattr__(
            self,
            "bulk_density",
            _validate_strictly_positive(self.bulk_density, "bulk_density"),
        )
        object.__setattr__(
            self,
            "ref_bulk_density",
            _validate_strictly_positive(self.ref_bulk_density, "ref_bulk_density"),
        )


@dataclass(frozen=True, slots=True)
class ChemicalProperties:
    """Groups vertical layer chemical and mineral measurements."""

    ph: float | None = None
    organic_carbon: float | None = None
    total_nitrogen: float | None = None
    cn_ratio: float | None = None
    cec_soil: float | None = None
    cec_clay: float | None = None
    effective_cec: float | None = None
    teb: float | None = None
    base_saturation: float | None = None
    aluminum_saturation: float | None = None
    esp: float | None = None
    calcium_carbonate: float | None = None
    gypsum: float | None = None
    electrical_conductivity: float | None = None

    def __post_init__(self) -> None:
        """Validate chemical soil properties."""
        # pH water bounds (0.0 to 14.0)
        f_ph = _check_float(self.ph, "ph")
        if f_ph is not None:
            if not (MIN_PH <= f_ph <= MAX_PH):
                raise InvalidLayerMeasurementsError(
                    f"pH must be between 0.0 and 14.0, got {f_ph}."
                )
            object.__setattr__(self, "ph", f_ph)

        # Non-negative properties
        object.__setattr__(
            self,
            "organic_carbon",
            _validate_non_negative(self.organic_carbon, "organic_carbon"),
        )
        object.__setattr__(
            self,
            "total_nitrogen",
            _validate_non_negative(self.total_nitrogen, "total_nitrogen"),
        )
        object.__setattr__(
            self, "cn_ratio", _validate_non_negative(self.cn_ratio, "cn_ratio")
        )
        object.__setattr__(
            self, "cec_soil", _validate_non_negative(self.cec_soil, "cec_soil")
        )
        object.__setattr__(
            self, "cec_clay", _validate_non_negative(self.cec_clay, "cec_clay")
        )
        object.__setattr__(
            self,
            "effective_cec",
            _validate_non_negative(self.effective_cec, "effective_cec"),
        )
        object.__setattr__(self, "teb", _validate_non_negative(self.teb, "teb"))
        object.__setattr__(
            self,
            "electrical_conductivity",
            _validate_non_negative(
                self.electrical_conductivity, "electrical_conductivity"
            ),
        )

        # Percentages
        object.__setattr__(
            self,
            "base_saturation",
            _validate_pct(self.base_saturation, "base_saturation"),
        )
        object.__setattr__(
            self,
            "aluminum_saturation",
            _validate_pct(self.aluminum_saturation, "aluminum_saturation"),
        )
        object.__setattr__(self, "esp", _validate_pct(self.esp, "esp"))
        object.__setattr__(
            self,
            "calcium_carbonate",
            _validate_pct(self.calcium_carbonate, "calcium_carbonate"),
        )
        object.__setattr__(self, "gypsum", _validate_pct(self.gypsum, "gypsum"))


@dataclass(frozen=True, slots=True)
class HydraulicProperties:
    """Groups vertical layer hydraulic measurements."""

    available_water_capacity: float | None = None

    def __post_init__(self) -> None:
        """Validate hydraulic soil properties."""
        object.__setattr__(
            self,
            "available_water_capacity",
            _validate_non_negative(
                self.available_water_capacity, "available_water_capacity"
            ),
        )


@dataclass(frozen=True, slots=True)
class LayerMeasurements:
    """Consolidates Physical, Chemical, and Hydraulic properties of a soil layer."""

    physical: PhysicalProperties
    chemical: ChemicalProperties
    hydraulic: HydraulicProperties

    def __post_init__(self) -> None:
        """Validate sub-property object types."""
        if not isinstance(self.physical, PhysicalProperties):
            raise InvalidLayerMeasurementsError(
                "physical must be a PhysicalProperties instance."
            )
        if not isinstance(self.chemical, ChemicalProperties):
            raise InvalidLayerMeasurementsError(
                "chemical must be a ChemicalProperties instance."
            )
        if not isinstance(self.hydraulic, HydraulicProperties):
            raise InvalidLayerMeasurementsError(
                "hydraulic must be a HydraulicProperties instance."
            )
