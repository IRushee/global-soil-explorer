"""Unit tests for the MDBReader component."""

from pathlib import Path

import pytest
from backend.processing.shared.mdb_reader import MDBReader

MDB_PATH = Path("../data/raw/hwsd/HWSD2.mdb")


def test_mdb_reader_file_not_found() -> None:
    """Verify that MDBReader raises FileNotFoundError for missing paths."""
    with pytest.raises(FileNotFoundError):
        MDBReader("nonexistent.mdb")


def test_mdb_reader_list_tables() -> None:
    """Verify that MDBReader lists tables correctly from the real database."""
    if not MDB_PATH.exists():
        pytest.skip("Real HWSD2.mdb database not found.")

    reader = MDBReader(MDB_PATH)
    tables = reader.list_tables()
    assert len(tables) > 0
    assert "HWSD2_LAYERS" in tables
    assert "D_WRB2" in tables


def test_mdb_reader_read_table() -> None:
    """Verify that MDBReader reads a table and parses types correctly."""
    if not MDB_PATH.exists():
        pytest.skip("Real HWSD2.mdb database not found.")

    reader = MDBReader(MDB_PATH)
    rows = reader.read_table("D_WRB2")
    assert len(rows) > 0
    first_row = rows[0]
    assert "CODE" in first_row
    assert "Value" in first_row
    assert isinstance(first_row["CODE"], str)
    assert isinstance(first_row["Value"], str)


def test_mdb_reader_primary_keys() -> None:
    """Verify that MDBReader parses primary keys correctly from the real database."""
    if not MDB_PATH.exists():
        pytest.skip("Real HWSD2.mdb database not found.")

    reader = MDBReader(MDB_PATH)
    assert reader.primary_keys.get("d_wrb2") == "code"
    assert reader.primary_keys.get("hwsd2_layers") == "id"
