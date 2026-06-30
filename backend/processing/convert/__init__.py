"""Conversion stage of the offline preprocessing pipeline."""

import logging

from backend.processing.shared.context import PreprocessingContext

logger = logging.getLogger(__name__)


def convert_database(context: PreprocessingContext) -> None:
    """Convert raw tabular database records to query-optimized formats.

    Args:
        context: The PreprocessingContext instance.
    """
    logger.info(
        "Converting tabular database formats for %s (v%s)",
        context.config.dataset_name,
        context.config.dataset_version,
    )
    # Placeholder for converting database tables (e.g. MDB -> SQLite)
    logger.info("Database conversion completed (placeholder).")
