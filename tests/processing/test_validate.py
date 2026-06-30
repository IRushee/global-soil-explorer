"""Unit tests for the raw dataset validation stage."""

import zipfile
from pathlib import Path

from backend.processing.validate import validate_hwsd_dataset


def test_validation_input_does_not_exist() -> None:
    """Verify that an input path that does not exist fails validation."""
    result = validate_hwsd_dataset(Path("/nonexistent/path/hwsd"))
    assert not result.is_valid
    assert any("does not exist" in err for err in result.errors)


def test_validation_input_invalid_file_type(tmp_path: Path) -> None:
    """Verify that a path that is not a directory or ZIP fails validation."""
    txt_file = tmp_path / "dummy.txt"
    txt_file.write_text("not a zip")
    result = validate_hwsd_dataset(txt_file)
    assert not result.is_valid
    assert any("neither a directory nor a ZIP" in err for err in result.errors)


def test_validation_valid_directory(tmp_path: Path) -> None:
    """Verify that a valid directory structure passes validation."""
    hdr_content = (
        "ncols          10\n"
        "nrows          20\n"
        "nbits          16\n"
        "nbands         1\n"
        "layout         bil\n"
    )
    (tmp_path / "hwsd.hdr").write_text(hdr_content)
    (tmp_path / "hwsd.prj").write_text("WGS84")
    (tmp_path / "hwsd.mdb").write_text("mdb content")
    # expected size: 10 cols * 20 rows * 2 bytes = 400 bytes
    (tmp_path / "hwsd.bil").write_bytes(b"\x00" * 400)

    result = validate_hwsd_dataset(tmp_path)
    assert result.is_valid
    assert len(result.errors) == 0
    assert result.metadata["ncols"] == 10
    assert result.metadata["nrows"] == 20
    assert result.metadata["nbits"] == 16


def test_validation_missing_required_files(tmp_path: Path) -> None:
    """Verify that missing required files fails validation."""
    (tmp_path / "hwsd.hdr").write_text("ncols 10\nnrows 10\nnbits 16\n")
    result = validate_hwsd_dataset(tmp_path)
    assert not result.is_valid
    assert any("missing in directory" in err for err in result.errors)


def test_validation_duplicate_files(tmp_path: Path) -> None:
    """Verify that duplicate files of the same extension fails validation."""
    (tmp_path / "hwsd.hdr").write_text("ncols 10\nnrows 10\nnbits 16\n")
    (tmp_path / "hwsd.prj").write_text("WGS84")
    (tmp_path / "hwsd.mdb").write_text("mdb")
    (tmp_path / "hwsd.bil").write_bytes(b"\x00" * 200)
    (tmp_path / "hwsd_dup.bil").write_bytes(b"\x00" * 200)

    result = validate_hwsd_dataset(tmp_path)
    assert not result.is_valid
    assert any("Duplicate BIL file found" in err for err in result.errors)


def test_validation_malformed_header(tmp_path: Path) -> None:
    """Verify that malformed or missing keys in HDR fails validation."""
    (tmp_path / "hwsd.hdr").write_text("ncols 10\n")
    (tmp_path / "hwsd.prj").write_text("WGS84")
    (tmp_path / "hwsd.mdb").write_text("mdb")
    (tmp_path / "hwsd.bil").write_bytes(b"\x00" * 200)

    result = validate_hwsd_dataset(tmp_path)
    assert not result.is_valid
    assert any("missing from HDR file" in err for err in result.errors)


def test_validation_size_mismatch(tmp_path: Path) -> None:
    """Verify that a size mismatch between BIL and HDR fails validation."""
    hdr_content = "ncols 10\nnrows 10\nnbits 16\n"
    (tmp_path / "hwsd.hdr").write_text(hdr_content)
    (tmp_path / "hwsd.prj").write_text("WGS84")
    (tmp_path / "hwsd.mdb").write_text("mdb")
    (tmp_path / "hwsd.bil").write_bytes(b"\x00" * 250)

    result = validate_hwsd_dataset(tmp_path)
    assert not result.is_valid
    assert any("does not match header dimensions" in err for err in result.errors)


def test_validation_valid_zip(tmp_path: Path) -> None:
    """Verify that a valid ZIP archive passes validation."""
    zip_file = tmp_path / "hwsd.zip"
    hdr_content = "ncols 10\nnrows 10\nnbits 8\n"

    with zipfile.ZipFile(zip_file, "w") as zf:
        zf.writestr("hwsd/hwsd.hdr", hdr_content)
        zf.writestr("hwsd/hwsd.prj", "WGS84")
        zf.writestr("hwsd/hwsd.mdb", "mdb content")
        zf.writestr("hwsd/hwsd.bil", b"\x00" * 100)

    result = validate_hwsd_dataset(zip_file)
    assert result.is_valid
    assert result.metadata["ncols"] == 10
    assert result.metadata["nrows"] == 10
    assert result.metadata["nbits"] == 8
