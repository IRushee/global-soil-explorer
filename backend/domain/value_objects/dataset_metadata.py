"""DatasetMetadata value object representing database source provenance."""

from dataclasses import dataclass

from backend.domain.exceptions import InvalidDatasetMetadataError


@dataclass(frozen=True, slots=True)
class DatasetMetadata:
    """Represents core data source provenance, standards, and references.

    Visualization information is strictly excluded from this value object.
    """

    coverage: int | None = None
    library: str | None = None
    source: str | None = None
    dataset_version: str | None = None
    reference_identifiers: tuple[tuple[str, str], ...] | None = None

    def __post_init__(self) -> None:
        """Validate metadata invariants."""
        if self.coverage is not None:
            if not isinstance(self.coverage, int) or isinstance(self.coverage, bool):
                raise InvalidDatasetMetadataError("coverage code must be an integer.")

        if self.library is not None:
            if not isinstance(self.library, str):
                raise InvalidDatasetMetadataError("library must be a string.")

        if self.source is not None:
            if not isinstance(self.source, str):
                raise InvalidDatasetMetadataError("source must be a string.")

        if self.dataset_version is not None:
            if not isinstance(self.dataset_version, str):
                raise InvalidDatasetMetadataError("dataset_version must be a string.")

        pair_length = 2
        if self.reference_identifiers is not None:
            if not isinstance(self.reference_identifiers, tuple):
                raise InvalidDatasetMetadataError(
                    "reference_identifiers must be a tuple of pairs."
                )
            for pair in self.reference_identifiers:
                if (
                    not isinstance(pair, tuple)
                    or len(pair) != pair_length
                    or not isinstance(pair[0], str)
                    or not isinstance(pair[1], str)
                ):
                    raise InvalidDatasetMetadataError(
                        "Each reference identifier must be a tuple "
                        "of exactly two strings."
                    )
