"""Preprocessing context holding validated dataset discovery and metadata state."""

from dataclasses import dataclass

from backend.processing.shared.config import PreprocessingConfig


@dataclass(frozen=True, slots=True)
class PreprocessingContext:
    """Immutable state containing the configuration and metadata.

    Holds the configuration, discovered files, and parsed metadata.
    """

    config: PreprocessingConfig
    discovered_paths: dict[str, str]
    metadata: dict[str, int | str]
    is_valid: bool
