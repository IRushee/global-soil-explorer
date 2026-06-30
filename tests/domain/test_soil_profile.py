"""Unit tests for the SoilProfile value object."""

from dataclasses import FrozenInstanceError

import pytest
from backend.domain import (
    InvalidProfileError,
    PropertyType,
    SoilClassification,
    SoilLayer,
    SoilProfile,
    SoilProperty,
    Unit,
)


@pytest.fixture
def sample_classification() -> SoilClassification:
    """Fixture for a standard SoilClassification."""
    return SoilClassification("WRB 2022", "ALfr", "Luvic Albeluvisol")


@pytest.fixture
def sample_property() -> SoilProperty:
    """Fixture for a standard SoilProperty."""
    return SoilProperty(PropertyType.PH_WATER, 6.5, Unit.PH)


@pytest.fixture
def sample_layers(
    sample_property: SoilProperty,
) -> tuple[SoilLayer, SoilLayer, SoilLayer]:
    """Fixture for three contiguous soil layers."""
    l1 = SoilLayer(0.0, 30.0, (sample_property,))
    l2 = SoilLayer(30.0, 60.0, (sample_property,))
    l3 = SoilLayer(60.0, 100.0, (sample_property,))
    return l1, l2, l3


def test_valid_profile(
    sample_classification: SoilClassification,
    sample_layers: tuple[SoilLayer, SoilLayer, SoilLayer],
) -> None:
    """Verify that a valid SoilProfile is successfully created."""
    l1, l2, l3 = sample_layers
    profile = SoilProfile(
        layers=(l1, l2, l3),
        classification=sample_classification,
        composition_share=60.0,
    )
    assert profile.layers == (l1, l2, l3)
    assert profile.classification == sample_classification
    assert profile.composition_share == 60.0


def test_single_layer_profile(
    sample_classification: SoilClassification,
    sample_layers: tuple[SoilLayer, SoilLayer, SoilLayer],
) -> None:
    """Verify that a profile with a single layer is valid."""
    l1, _, _ = sample_layers
    profile = SoilProfile(
        layers=(l1,),
        classification=sample_classification,
    )
    assert profile.layers == (l1,)
    assert profile.composition_share is None


def test_multiple_valid_layers(
    sample_classification: SoilClassification,
    sample_layers: tuple[SoilLayer, SoilLayer, SoilLayer],
) -> None:
    """Verify that a list of layers is coerced to a tuple and validation passes."""
    l1, l2, l3 = sample_layers
    profile = SoilProfile(
        layers=[l1, l2, l3],  # type: ignore[arg-type]
        classification=sample_classification,
    )
    assert isinstance(profile.layers, tuple)
    assert profile.layers == (l1, l2, l3)


def test_invalid_layers_structure_type(
    sample_classification: SoilClassification,
) -> None:
    """Verify that invalid types for the layers collection raise InvalidProfileError."""
    with pytest.raises(InvalidProfileError, match="layers must be a tuple or list"):
        SoilProfile(layers="not a sequence", classification=sample_classification)  # type: ignore[arg-type]


def test_invalid_layer_elements(
    sample_classification: SoilClassification,
    sample_layers: tuple[SoilLayer, SoilLayer, SoilLayer],
) -> None:
    """Verify that non-SoilLayer elements inside layers raise InvalidProfileError."""
    l1, _, _ = sample_layers
    with pytest.raises(
        InvalidProfileError, match="All elements in layers must be SoilLayer"
    ):
        SoilProfile(layers=(l1, "not a layer"), classification=sample_classification)  # type: ignore[arg-type]


def test_empty_layers(sample_classification: SoilClassification) -> None:
    """Verify that an empty layers sequence is rejected."""
    with pytest.raises(
        InvalidProfileError, match="must contain at least one layer"
    ):
        SoilProfile(layers=(), classification=sample_classification)



def test_invalid_classification_type(
    sample_layers: tuple[SoilLayer, SoilLayer, SoilLayer],
) -> None:
    """Verify that invalid classification type raises InvalidProfileError."""
    l1, _, _ = sample_layers
    with pytest.raises(
        InvalidProfileError, match="classification must be a SoilClassification"
    ):
        SoilProfile(layers=(l1,), classification="not a classification")  # type: ignore[arg-type]


def test_invalid_composition_share_types(
    sample_classification: SoilClassification,
    sample_layers: tuple[SoilLayer, SoilLayer, SoilLayer],
) -> None:
    """Verify that invalid types for composition_share raise InvalidProfileError."""
    l1, _, _ = sample_layers
    with pytest.raises(
        InvalidProfileError, match="composition_share must be a numeric value"
    ):
        SoilProfile(
            layers=(l1,),
            classification=sample_classification,
            composition_share="50",  # type: ignore[arg-type]
        )

    with pytest.raises(
        InvalidProfileError, match="composition_share must be a numeric value"
    ):
        SoilProfile(
            layers=(l1,),
            classification=sample_classification,
            composition_share=True,
        )



def test_non_finite_composition_share(
    sample_classification: SoilClassification,
    sample_layers: tuple[SoilLayer, SoilLayer, SoilLayer],
) -> None:
    """Verify that non-finite values for composition_share are rejected."""
    l1, _, _ = sample_layers
    with pytest.raises(
        InvalidProfileError, match="composition_share must be a finite number"
    ):
        SoilProfile(
            layers=(l1,),
            classification=sample_classification,
            composition_share=float("nan"),
        )

    with pytest.raises(
        InvalidProfileError, match="composition_share must be a finite number"
    ):
        SoilProfile(
            layers=(l1,),
            classification=sample_classification,
            composition_share=float("inf"),
        )


def test_composition_share_bounds(
    sample_classification: SoilClassification,
    sample_layers: tuple[SoilLayer, SoilLayer, SoilLayer],
) -> None:
    """Verify that composition_share values out of range [0, 100] are rejected."""
    l1, _, _ = sample_layers
    with pytest.raises(
        InvalidProfileError, match="composition_share must be between 0.0 and 100.0"
    ):
        SoilProfile(
            layers=(l1,),
            classification=sample_classification,
            composition_share=-0.1,
        )

    with pytest.raises(
        InvalidProfileError, match="composition_share must be between 0.0 and 100.0"
    ):
        SoilProfile(
            layers=(l1,),
            classification=sample_classification,
            composition_share=100.1,
        )

    # Boundary cases should succeed
    p_min = SoilProfile(
        layers=(l1,),
        classification=sample_classification,
        composition_share=0.0,
    )
    assert p_min.composition_share == 0.0

    p_max = SoilProfile(
        layers=(l1,),
        classification=sample_classification,
        composition_share=100.0,
    )
    assert p_max.composition_share == 100.0


def test_unordered_layers(
    sample_classification: SoilClassification,
    sample_layers: tuple[SoilLayer, SoilLayer, SoilLayer],
) -> None:
    """Verify that layers not ordered by depth raise InvalidProfileError."""
    l1, l2, l3 = sample_layers
    # Correct order: l1 (0-30), l2 (30-60), l3 (60-100)
    with pytest.raises(InvalidProfileError, match="Layers overlap or are out of order"):
        SoilProfile(
            layers=(l2, l1, l3),
            classification=sample_classification,
        )


def test_overlapping_layers(
    sample_classification: SoilClassification,
    sample_property: SoilProperty,
) -> None:
    """Verify that overlapping layers raise InvalidProfileError."""
    l1 = SoilLayer(0.0, 30.0, (sample_property,))
    l_overlap = SoilLayer(25.0, 60.0, (sample_property,))

    with pytest.raises(InvalidProfileError, match="Layers overlap or are out of order"):
        SoilProfile(
            layers=(l1, l_overlap),
            classification=sample_classification,
        )


def test_touching_layers(
    sample_classification: SoilClassification,
    sample_layers: tuple[SoilLayer, SoilLayer, SoilLayer],
) -> None:
    """Verify that touching layer boundaries are allowed."""
    l1, l2, _ = sample_layers
    # l1.bottom (30.0) == l2.top (30.0)
    profile = SoilProfile(
        layers=(l1, l2),
        classification=sample_classification,
    )
    assert profile.layers == (l1, l2)


def test_gapped_layers(
    sample_classification: SoilClassification,
    sample_property: SoilProperty,
) -> None:
    """Verify that gaps between layer depths are allowed and not interpolated."""
    l1 = SoilLayer(0.0, 30.0, (sample_property,))
    l2 = SoilLayer(40.0, 60.0, (sample_property,))  # Gap of 10cm (30 to 40)

    profile = SoilProfile(
        layers=(l1, l2),
        classification=sample_classification,
    )
    assert profile.layers == (l1, l2)


def test_immutability(
    sample_classification: SoilClassification,
    sample_layers: tuple[SoilLayer, SoilLayer, SoilLayer],
) -> None:
    """Verify that SoilProfile attributes cannot be modified post-creation."""
    l1, _, _ = sample_layers
    profile = SoilProfile(
        layers=(l1,),
        classification=sample_classification,
        composition_share=50.0,
    )

    with pytest.raises(FrozenInstanceError):
        profile.layers = ()  # type: ignore[misc]

    with pytest.raises(FrozenInstanceError):
        profile.classification = sample_classification  # type: ignore[misc]

    with pytest.raises(FrozenInstanceError):
        profile.composition_share = 60.0  # type: ignore[misc]


def test_equality(
    sample_classification: SoilClassification,
    sample_layers: tuple[SoilLayer, SoilLayer, SoilLayer],
) -> None:
    """Verify standard dataclass structural equality."""
    l1, l2, _ = sample_layers
    p1 = SoilProfile(
        layers=(l1, l2),
        classification=sample_classification,
        composition_share=50.0,
    )
    p2 = SoilProfile(
        layers=(l1, l2),
        classification=sample_classification,
        composition_share=50.0,
    )
    p3 = SoilProfile(
        layers=(l1,),
        classification=sample_classification,
        composition_share=50.0,
    )
    p4 = SoilProfile(
        layers=(l1, l2),
        classification=sample_classification,
        composition_share=60.0,
    )

    assert p1 == p2
    assert p1 != p3
    assert p1 != p4


def test_hashability(
    sample_classification: SoilClassification,
    sample_layers: tuple[SoilLayer, SoilLayer, SoilLayer],
) -> None:
    """Verify SoilProfile is hashable and works in sets/dicts."""
    l1, l2, _ = sample_layers
    p1 = SoilProfile(
        layers=(l1, l2),
        classification=sample_classification,
        composition_share=50.0,
    )
    p2 = SoilProfile(
        layers=(l1, l2),
        classification=sample_classification,
        composition_share=50.0,
    )
    p3 = SoilProfile(
        layers=(l1,),
        classification=sample_classification,
        composition_share=None,
    )

    profile_set = {p1, p2, p3}
    assert len(profile_set) == 2
    assert p1 in profile_set
    assert p3 in profile_set


def test_slots(
    sample_classification: SoilClassification,
    sample_layers: tuple[SoilLayer, SoilLayer, SoilLayer],
) -> None:
    """Verify that SoilProfile has slots and no __dict__ representation."""
    l1, _, _ = sample_layers
    profile = SoilProfile(
        layers=(l1,),
        classification=sample_classification,
    )
    assert not hasattr(profile, "__dict__")
