"""Unit tests for the newly added scientific domain value objects."""

from dataclasses import FrozenInstanceError

import pytest

from backend.domain import (
    ChemicalProperties,
    DatasetMetadata,
    EnvironmentalContext,
    HydraulicProperties,
    HydrologicContext,
    InvalidDatasetMetadataError,
    InvalidEnvironmentalContextError,
    InvalidHydrologicContextError,
    InvalidLandLimitationsError,
    InvalidLayerMeasurementsError,
    InvalidSoilTextureError,
    LandLimitations,
    LayerMeasurements,
    PhysicalProperties,
    SoilTexture,
)


# === 1. EnvironmentalContext Tests ===
def test_environmental_context_valid() -> None:
    """Verify valid EnvironmentalContext instantiation."""
    ctx = EnvironmentalContext(koppen_climate="A")
    assert ctx.koppen_climate == "A"

    ctx_none = EnvironmentalContext(koppen_climate=None)
    assert ctx_none.koppen_climate is None

    # Verify whitespace strip and case normalization
    ctx_strip = EnvironmentalContext(koppen_climate=" b ")
    assert ctx_strip.koppen_climate == "B"


def test_environmental_context_invalid() -> None:
    """Verify invalid EnvironmentalContext constraints."""
    with pytest.raises(InvalidEnvironmentalContextError):
        EnvironmentalContext(koppen_climate="Z")

    with pytest.raises(InvalidEnvironmentalContextError):
        EnvironmentalContext(koppen_climate=123)  # type: ignore


def test_environmental_context_immutability() -> None:
    """Verify EnvironmentalContext is frozen."""
    ctx = EnvironmentalContext(koppen_climate="A")
    with pytest.raises(FrozenInstanceError):
        ctx.koppen_climate = "B"  # type: ignore


def test_environmental_context_equality_and_hash() -> None:
    """Verify equality and hash implementation."""
    ctx1 = EnvironmentalContext(koppen_climate="A")
    ctx2 = EnvironmentalContext(koppen_climate="A")
    ctx3 = EnvironmentalContext(koppen_climate="B")

    assert ctx1 == ctx2
    assert ctx1 != ctx3
    assert hash(ctx1) == hash(ctx2)
    assert hash(ctx1) != hash(ctx3)


# === 2. HydrologicContext Tests ===
def test_hydrologic_context_valid() -> None:
    """Verify valid HydrologicContext instantiation."""
    ctx = HydrologicContext(drainage="MW", water_regime=2, impermeable_layer=4)
    assert ctx.drainage == "MW"
    assert ctx.water_regime == 2
    assert ctx.impermeable_layer == 4

    ctx_empty = HydrologicContext()
    assert ctx_empty.drainage is None
    assert ctx_empty.water_regime is None
    assert ctx_empty.impermeable_layer is None


def test_hydrologic_context_invalid() -> None:
    """Verify invalid HydrologicContext invariants."""
    # Invalid Drainage
    with pytest.raises(InvalidHydrologicContextError):
        HydrologicContext(drainage="XYZ")

    with pytest.raises(InvalidHydrologicContextError):
        HydrologicContext(drainage=123)  # type: ignore

    # Invalid water regime
    with pytest.raises(InvalidHydrologicContextError):
        HydrologicContext(water_regime=5)

    with pytest.raises(InvalidHydrologicContextError):
        HydrologicContext(water_regime="2")  # type: ignore

    # Invalid impermeable layer
    with pytest.raises(InvalidHydrologicContextError):
        HydrologicContext(impermeable_layer=9)


def test_hydrologic_context_immutability_and_hash() -> None:
    """Verify HydrologicContext is frozen and hashable."""
    ctx = HydrologicContext(drainage="W", water_regime=1)
    with pytest.raises(FrozenInstanceError):
        ctx.drainage = "MW"  # type: ignore

    ctx2 = HydrologicContext(drainage="W", water_regime=1)
    assert ctx == ctx2
    assert hash(ctx) == hash(ctx2)


# === 3. LandLimitations Tests ===
def test_land_limitations_valid() -> None:
    """Verify valid LandLimitations instantiation."""
    limits = LandLimitations(
        root_depth=2, root_obstacles=4, phase1=10, phase2=30, additional_property=1
    )
    assert limits.root_depth == 2
    assert limits.root_obstacles == 4
    assert limits.phase1 == 10
    assert limits.phase2 == 30
    assert limits.additional_property == 1


def test_land_limitations_invalid() -> None:
    """Verify invalid LandLimitations constraints."""
    with pytest.raises(InvalidLandLimitationsError):
        LandLimitations(root_depth=5)

    with pytest.raises(InvalidLandLimitationsError):
        LandLimitations(root_obstacles=7)

    with pytest.raises(InvalidLandLimitationsError):
        LandLimitations(phase1=-1)

    with pytest.raises(InvalidLandLimitationsError):
        LandLimitations(phase2=31)

    with pytest.raises(InvalidLandLimitationsError):
        LandLimitations(additional_property=4)


def test_land_limitations_immutability() -> None:
    """Verify LandLimitations immutability and hash."""
    limits = LandLimitations(root_depth=1)
    with pytest.raises(FrozenInstanceError):
        limits.root_depth = 2  # type: ignore
    limits2 = LandLimitations(root_depth=1)
    assert limits == limits2
    assert hash(limits) == hash(limits2)


# === 4. SoilTexture Tests ===
def test_soil_texture_valid() -> None:
    """Verify valid SoilTexture instantiation."""
    tex = SoilTexture(usda_texture=9, soter_texture="Z")
    assert tex.usda_texture == 9
    assert tex.soter_texture == "Z"


def test_soil_texture_invalid() -> None:
    """Verify invalid SoilTexture constraints."""
    with pytest.raises(InvalidSoilTextureError):
        SoilTexture(usda_texture=15)

    with pytest.raises(InvalidSoilTextureError):
        SoilTexture(soter_texture="A")


def test_soil_texture_immutability() -> None:
    """Verify SoilTexture immutability."""
    tex = SoilTexture(usda_texture=1)
    with pytest.raises(FrozenInstanceError):
        tex.usda_texture = 2  # type: ignore
    assert tex == SoilTexture(usda_texture=1)
    assert hash(tex) == hash(SoilTexture(usda_texture=1))


# === 5. LayerMeasurements & Properties Tests ===
def test_physical_properties_valid() -> None:
    """Verify valid PhysicalProperties."""
    phys = PhysicalProperties(
        sand=40.0,
        silt=30.0,
        clay=30.0,
        coarse_fragments=15.0,
        bulk_density=1.4,
        ref_bulk_density=1.35,
    )
    assert phys.sand == 40.0
    assert phys.bulk_density == 1.4


def test_physical_properties_invalid() -> None:
    """Verify invalid PhysicalProperties constraints."""
    # Out of bounds percentage
    with pytest.raises(InvalidLayerMeasurementsError):
        PhysicalProperties(sand=100.5)

    with pytest.raises(InvalidLayerMeasurementsError):
        PhysicalProperties(silt=-0.1)

    # Bulk density non-positive
    with pytest.raises(InvalidLayerMeasurementsError):
        PhysicalProperties(bulk_density=0.0)

    with pytest.raises(InvalidLayerMeasurementsError):
        PhysicalProperties(ref_bulk_density=-0.2)

    # Non-finite values
    with pytest.raises(InvalidLayerMeasurementsError):
        PhysicalProperties(sand=float("nan"))

    with pytest.raises(InvalidLayerMeasurementsError):
        PhysicalProperties(clay=float("inf"))


def test_chemical_properties_valid() -> None:
    """Verify valid ChemicalProperties."""
    chem = ChemicalProperties(
        ph=6.5,
        organic_carbon=2.5,
        total_nitrogen=0.2,
        cn_ratio=12.5,
        cec_soil=18.0,
        cec_clay=24.0,
        effective_cec=15.0,
        teb=12.0,
        base_saturation=80.0,
        aluminum_saturation=5.0,
        esp=2.0,
        calcium_carbonate=4.0,
        gypsum=1.0,
        electrical_conductivity=0.8,
    )
    assert chem.ph == 6.5
    assert chem.organic_carbon == 2.5
    assert chem.cn_ratio == 12.5


def test_chemical_properties_invalid() -> None:
    """Verify invalid ChemicalProperties constraints."""
    # Out of bounds pH
    with pytest.raises(InvalidLayerMeasurementsError):
        ChemicalProperties(ph=14.1)

    # Negative values
    with pytest.raises(InvalidLayerMeasurementsError):
        ChemicalProperties(organic_carbon=-0.1)

    with pytest.raises(InvalidLayerMeasurementsError):
        ChemicalProperties(total_nitrogen=-0.01)

    # Out of bounds percentages
    with pytest.raises(InvalidLayerMeasurementsError):
        ChemicalProperties(base_saturation=101.0)

    with pytest.raises(InvalidLayerMeasurementsError):
        ChemicalProperties(esp=-1.0)


def test_hydraulic_properties_valid_and_invalid() -> None:
    """Verify HydraulicProperties invariants."""
    hyd = HydraulicProperties(available_water_capacity=150.0)
    assert hyd.available_water_capacity == 150.0

    with pytest.raises(InvalidLayerMeasurementsError):
        HydraulicProperties(available_water_capacity=-1.0)


def test_layer_measurements_composition() -> None:
    """Verify LayerMeasurements consolidates all properties and remains immutable."""
    phys = PhysicalProperties(sand=40.0)
    chem = ChemicalProperties(ph=6.0)
    hyd = HydraulicProperties(available_water_capacity=100.0)

    measure = LayerMeasurements(physical=phys, chemical=chem, hydraulic=hyd)
    assert measure.physical == phys
    assert measure.chemical == chem
    assert measure.hydraulic == hyd

    # Test type checking on sub-objects
    with pytest.raises(InvalidLayerMeasurementsError):
        LayerMeasurements(physical="invalid", chemical=chem, hydraulic=hyd)  # type: ignore

    with pytest.raises(FrozenInstanceError):
        measure.physical = phys  # type: ignore


# === 6. DatasetMetadata Tests ===
def test_dataset_metadata_valid() -> None:
    """Verify valid DatasetMetadata creation."""
    meta = DatasetMetadata(
        coverage=1,
        library="HWSD",
        source="FAO",
        dataset_version="v2.0",
        reference_identifiers=(("DOI", "10.5061/dryad"),),
    )
    assert meta.coverage == 1
    assert meta.library == "HWSD"
    assert meta.reference_identifiers == (("DOI", "10.5061/dryad"),)


def test_dataset_metadata_invalid() -> None:
    """Verify invalid DatasetMetadata validation."""
    with pytest.raises(InvalidDatasetMetadataError):
        DatasetMetadata(coverage="invalid")  # type: ignore

    with pytest.raises(InvalidDatasetMetadataError):
        DatasetMetadata(library=123)  # type: ignore

    with pytest.raises(InvalidDatasetMetadataError):
        DatasetMetadata(reference_identifiers="not-a-tuple")  # type: ignore

    with pytest.raises(InvalidDatasetMetadataError):
        DatasetMetadata(reference_identifiers=((123, "val"),))  # type: ignore
