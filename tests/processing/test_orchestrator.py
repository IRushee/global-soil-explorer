"""Unit tests for the preprocessing pipeline orchestrator."""

from pathlib import Path

import pytest
from backend.processing.main import run_preprocessing_pipeline
from backend.processing.shared.config import PreprocessingConfig
from backend.processing.shared.context import PreprocessingContext


def test_pipeline_orchestrator_success(tmp_path: Path) -> None:
    """Verify that a valid raw directory executes the full pipeline orchestrator."""
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    out_dir = tmp_path / "out"
    out_dir.mkdir()

    hdr_content = "ncols          5\nnrows          10\nnbits          16\n"
    (raw_dir / "hwsd.hdr").write_text(hdr_content)
    (raw_dir / "hwsd.prj").write_text("WGS84")
    (raw_dir / "hwsd.mdb").write_text("mdb content")
    # expected size: 5 cols * 10 rows * 2 bytes = 100 bytes
    (raw_dir / "hwsd.bil").write_bytes(b"\x00" * 100)

    config = PreprocessingConfig(raw_data_dir=raw_dir, output_dir=out_dir)

    context = run_preprocessing_pipeline(config)

    assert isinstance(context, PreprocessingContext)
    assert context.is_valid
    assert context.config == config
    assert "bil" in context.discovered_paths
    assert context.metadata["ncols"] == 5
    assert context.metadata["nrows"] == 10
    assert context.metadata["nbits"] == 16


def test_pipeline_orchestrator_failure(tmp_path: Path) -> None:
    """Verify that an invalid raw directory fails validation in the orchestrator."""
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    out_dir = tmp_path / "out"
    out_dir.mkdir()

    config = PreprocessingConfig(raw_data_dir=raw_dir, output_dir=out_dir)

    with pytest.raises(ValueError, match="Dataset validation failed"):
        run_preprocessing_pipeline(config)
