"""Configuration and models for the offline preprocessing pipeline."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class PreprocessingConfig:
    """Configuration settings for the preprocessing pipeline stages."""

    raw_data_dir: Path
    output_dir: Path
    dataset_name: str = "hwsd"
    dataset_version: str = "2.0"
