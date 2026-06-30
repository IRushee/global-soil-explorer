"""Main orchestrator for the offline preprocessing pipeline."""

import argparse
import logging
import sys
from pathlib import Path

from backend.processing.convert import convert_database
from backend.processing.extract import extract_archive
from backend.processing.generate import generate_runtime_assets
from backend.processing.shared.config import PreprocessingConfig
from backend.processing.validate import validate_dataset

# Setup logger configuration for the pipeline execution
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("backend.processing.main")


def run_preprocessing_pipeline(config: PreprocessingConfig) -> None:
    """Orchestrate the preprocessing pipeline stages sequentially.

    Args:
        config: The PreprocessingConfig instance.
    """
    logger.info("Initializing offline preprocessing pipeline...")

    # 1. Extraction Stage
    extract_archive(config)

    # 2. Validation Stage
    validate_dataset(config)

    # 3. Database Conversion Stage
    convert_database(config)

    # 4. Runtime Asset Generation Stage
    generate_runtime_assets(config)

    logger.info("Offline preprocessing pipeline successfully completed.")


def main() -> None:
    """CLI parser and entry point for offline preprocessing."""
    parser = argparse.ArgumentParser(
        description="Global Soil Explorer Offline Preprocessing Pipeline"
    )
    parser.add_argument(
        "--raw-dir",
        type=str,
        required=True,
        help="Directory path containing raw data files.",
    )
    parser.add_argument(
        "--out-dir",
        type=str,
        required=True,
        help="Directory path where generated assets will be stored.",
    )

    args = parser.parse_args()

    config = PreprocessingConfig(
        raw_data_dir=Path(args.raw_dir),
        output_dir=Path(args.out_dir),
    )

    run_preprocessing_pipeline(config)


if __name__ == "__main__":
    main()
