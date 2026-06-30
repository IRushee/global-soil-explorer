"""Generation stage of the offline preprocessing pipeline."""

import logging

from backend.processing.shared.config import PreprocessingConfig

logger = logging.getLogger(__name__)


def generate_runtime_assets(config: PreprocessingConfig) -> None:
    """Generate final query-optimized runtime files and indexes.

    Args:
        config: The PreprocessingConfig instance.
    """
    logger.info(
        "Generating runtime query assets for %s (v%s) in %s",
        config.dataset_name,
        config.dataset_version,
        config.output_dir,
    )
    # Placeholder for extracting/arranging raster grids and indexes
    logger.info("Runtime asset generation completed (placeholder).")
