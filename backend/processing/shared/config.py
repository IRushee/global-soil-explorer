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

    def __post_init__(self) -> None:
        """Coerce directory paths to Path objects if passed as strings."""
        if not isinstance(self.raw_data_dir, Path):
            object.__setattr__(self, "raw_data_dir", Path(self.raw_data_dir))
        if not isinstance(self.output_dir, Path):
            object.__setattr__(self, "output_dir", Path(self.output_dir))
