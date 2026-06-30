"""Conversion stage of the offline preprocessing pipeline."""

import logging

from backend.processing.shared.config import PreprocessingConfig

logger = logging.getLogger(__name__)


def convert_database(config: PreprocessingConfig) -> None:
    """Convert raw tabular database records to query-optimized formats.

    Args:
        config: The PreprocessingConfig instance.
    """
    logger.info(
        "Converting tabular database formats for %s (v%s)",
        config.dataset_name,
        config.dataset_version,
    )
    # Placeholder for converting database tables (e.g. MDB -> SQLite)
    logger.info("Database conversion completed (placeholder).")
