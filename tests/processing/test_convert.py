"""Unit tests for the processed database generation stage."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest
from backend.processing.convert import clean_value, convert_database
from backend.processing.shared.config import PreprocessingConfig
from backend.processing.shared.context import PreprocessingContext


def test_clean_value_sentinels() -> None:
    """Verify that clean_value maps sentinel codes to None."""
    assert clean_value(-9) is None
    assert clean_value(-99) is None
    assert clean_value(-9999) is None
    assert clean_value(-9.0) is None
    assert clean_value("-99") is None
    assert clean_value("-99.0") is None

    # Valid values should be untouched
    assert clean_value(6.5) == 6.5
    assert clean_value(0) == 0
    assert clean_value("AC") == "AC"


def test_convert_database_flow(tmp_path: Path) -> None:
    """Verify that convert_database coordinates MDBReader and validates."""
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    out_dir = tmp_path / "out"
    out_dir.mkdir()

    config = PreprocessingConfig(raw_data_dir=raw_dir, output_dir=out_dir)
    context = PreprocessingContext(
        config=config,
        discovered_paths={"mdb": str(raw_dir / "HWSD2.mdb")},
        metadata={},
        is_valid=True,
    )

    with pytest.MonkeyPatch.context() as mp:
        mock_reader = MagicMock()
        mp.setattr("backend.processing.convert.MDBReader", lambda path: mock_reader)

        mock_reader.list_tables.return_value = ["D_WRB2"]
        mock_reader.read_table.return_value = [{"CODE": "AC", "Value": "Acrisols"}]
        mock_reader.primary_keys = {"d_wrb2": "code"}
        mock_reader._schema = {"d_wrb2": {"code": "text", "value": "text"}}

        convert_database(context)

        # Verify SQLite file was created and is valid
        db_file = out_dir / "hwsd.db"
        assert db_file.exists()
        assert db_file.stat().st_size > 0
