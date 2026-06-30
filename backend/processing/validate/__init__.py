"""Validation stage of the offline preprocessing pipeline."""

import logging

from backend.processing.shared.config import PreprocessingConfig

logger = logging.getLogger(__name__)


def validate_dataset(config: PreprocessingConfig) -> None:
    """Perform structural and metadata validation checks on raw data.

    Args:
        config: The PreprocessingConfig instance.
    """
    logger.info(
        "Validating raw %s (v%s) datasets in %s",
        config.dataset_name,
        config.dataset_version,
        config.raw_data_dir,
    )
    # Placeholder for file presence, format, metadata and CRS validation
    logger.info("Validation checks completed (placeholder).")
