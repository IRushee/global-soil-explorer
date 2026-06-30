"""Extraction stage of the offline preprocessing pipeline."""

import logging

from backend.processing.shared.config import PreprocessingConfig

logger = logging.getLogger(__name__)


def extract_archive(config: PreprocessingConfig) -> None:
    """Extract raw compressed dataset archives.

    Args:
        config: The PreprocessingConfig instance.
    """
    logger.info(
        "Starting extraction of %s (v%s) from %s",
        config.dataset_name,
        config.dataset_version,
        config.raw_data_dir,
    )
    # Placeholder for dataset extraction logic
    logger.info("Extraction completed (placeholder).")
