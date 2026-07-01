"""Validation stage of the offline preprocessing pipeline."""

import logging
import zipfile
from dataclasses import dataclass
from pathlib import Path

from backend.processing.shared.config import PreprocessingConfig

logger = logging.getLogger(__name__)

# Constants for validation limits
MIN_PARTS_COUNT = 2
SUPPORTED_NBITS = {8, 16, 32}


@dataclass(frozen=True, slots=True)
class ValidationResult:
    """Result of raw dataset structure and metadata validation checks."""

    is_valid: bool
    errors: tuple[str, ...]
    warnings: tuple[str, ...]
    discovered_paths: dict[str, str]
    metadata: dict[str, int | str]


def _parse_hdr_content(hdr_content: str) -> dict[str, int | str]:
    """Parse key-value pairs from .hdr metadata content."""
    metadata: dict[str, int | str] = {}
    for raw_line in hdr_content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.replace("=", " ").split()
        if len(parts) >= MIN_PARTS_COUNT:
            key = parts[0].lower()
            val_str = parts[1]
            if val_str.isdigit():
                metadata[key] = int(val_str)
            else:
                metadata[key] = val_str
    return metadata


def _validate_header_metadata(
    metadata: dict[str, int | str], errors: list[str]
) -> None:
    """Validate numeric boundaries and presence of required metadata fields."""
    for req_key in ("nrows", "ncols", "nbits"):
        if req_key not in metadata:
            errors.append(
                f"Required header key '{req_key.upper()}' is missing from HDR file."
            )

    if errors:
        return

    nrows = metadata["nrows"]
    ncols = metadata["ncols"]
    nbits = metadata["nbits"]
    nbands = metadata.get("nbands", 1)

    if not isinstance(nrows, int) or nrows <= 0:
        errors.append(f"Invalid nrows value in HDR: {nrows}")
    if not isinstance(ncols, int) or ncols <= 0:
        errors.append(f"Invalid ncols value in HDR: {ncols}")
    if not isinstance(nbits, int) or nbits not in SUPPORTED_NBITS:
        errors.append(f"Invalid or unsupported nbits value in HDR: {nbits}")
    if not isinstance(nbands, int) or nbands <= 0:
        errors.append(f"Invalid nbands value in HDR: {nbands}")


def _discover_files_in_directory(dir_path: Path, errors: list[str]) -> dict[str, str]:
    """Discover required files in a directory and check for duplicates."""
    discovered: dict[str, str] = {}
    try:
        for path in dir_path.rglob("*"):
            if not path.is_file():
                continue
            ext = path.suffix.lower()[1:]
            if ext in {"bil", "hdr", "prj", "mdb"}:
                if ext in discovered:
                    errors.append(
                        f"Duplicate {ext.upper()} file found in directory: "
                        f"'{path}' and '{discovered[ext]}'."
                    )
                else:
                    discovered[ext] = str(path.resolve())

        for ext in ("bil", "hdr", "prj", "mdb"):
            if ext not in discovered:
                errors.append(
                    f"Required file with extension .{ext} is missing in directory."
                )
    except Exception as e:
        errors.append(f"Failed to scan directory: {e}")
    return discovered


def _check_files_readability(discovered: dict[str, str], errors: list[str]) -> None:
    """Verify that discovered files (excluding the header) are readable."""
    for ext, path_str in discovered.items():
        if ext == "hdr":
            continue
        p = Path(path_str)
        try:
            with open(p, "rb") as f:
                f.read(1024)
        except Exception as e:
            errors.append(f"File '{p}' is not readable: {e}")


def _validate_zip_archive(zip_path: Path) -> ValidationResult:
    """Validate required files inside a ZIP archive without extracting them."""
    errors: list[str] = []
    warnings: list[str] = []
    discovered: dict[str, str] = {}
    metadata: dict[str, int | str] = {}

    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            for member in zf.infolist():
                if member.is_dir():
                    continue
                ext = Path(member.filename).suffix.lower()[1:]
                if ext in {"bil", "hdr", "prj", "mdb"}:
                    if ext in discovered:
                        errors.append(
                            f"Duplicate {ext.upper()} file found in ZIP: "
                            f"'{member.filename}' and '{discovered[ext]}'."
                        )
                    else:
                        discovered[ext] = member.filename

            for ext in ("bil", "hdr", "prj", "mdb"):
                if ext not in discovered:
                    errors.append(
                        f"Required file with extension .{ext} is missing in ZIP."
                    )

            if errors:
                return ValidationResult(
                    False,
                    tuple(errors),
                    tuple(warnings),
                    discovered,
                    metadata,
                )

            hdr_filename = discovered["hdr"]
            try:
                with zf.open(hdr_filename) as f:
                    hdr_content = f.read().decode("utf-8", errors="replace")
            except Exception as e:
                errors.append(f"Failed to read HDR file '{hdr_filename}' in ZIP: {e}")
                return ValidationResult(
                    False,
                    tuple(errors),
                    tuple(warnings),
                    discovered,
                    metadata,
                )

            metadata.update(_parse_hdr_content(hdr_content))
            _validate_header_metadata(metadata, errors)

            if not errors:
                nrows = int(metadata["nrows"])
                ncols = int(metadata["ncols"])
                nbits = int(metadata["nbits"])
                nbands = int(metadata.get("nbands", 1))

                expected_size = nrows * ncols * (nbits // 8) * nbands
                bil_member = zf.getinfo(discovered["bil"])
                actual_size = bil_member.file_size
                if actual_size != expected_size:
                    errors.append(
                        f"BIL file size ({actual_size} bytes) does not match "
                        f"header dimensions ({expected_size} bytes)."
                    )

    except Exception as e:
        errors.append(f"Failed to process ZIP archive: {e}")

    is_valid = len(errors) == 0
    return ValidationResult(
        is_valid, tuple(errors), tuple(warnings), discovered, metadata
    )


def _validate_directory(dir_path: Path) -> ValidationResult:
    """Validate required files inside a directory structure."""
    errors: list[str] = []
    warnings: list[str] = []
    metadata: dict[str, int | str] = {}

    discovered = _discover_files_in_directory(dir_path, errors)
    if errors:
        return ValidationResult(
            False, tuple(errors), tuple(warnings), discovered, metadata
        )

    hdr_path = Path(discovered["hdr"])
    try:
        with open(hdr_path, encoding="utf-8", errors="replace") as f:
            hdr_content = f.read()
    except Exception as e:
        errors.append(f"Failed to read HDR file '{hdr_path}': {e}")
        return ValidationResult(
            False, tuple(errors), tuple(warnings), discovered, metadata
        )

    _check_files_readability(discovered, errors)
    if errors:
        return ValidationResult(
            False, tuple(errors), tuple(warnings), discovered, metadata
        )

    metadata.update(_parse_hdr_content(hdr_content))
    _validate_header_metadata(metadata, errors)

    if not errors:
        nrows = int(metadata["nrows"])
        ncols = int(metadata["ncols"])
        nbits = int(metadata["nbits"])
        nbands = int(metadata.get("nbands", 1))

        expected_size = nrows * ncols * (nbits // 8) * nbands
        bil_path = Path(discovered["bil"])
        actual_size = bil_path.stat().st_size
        if actual_size != expected_size:
            errors.append(
                f"BIL file size ({actual_size} bytes) does not match "
                f"header dimensions ({expected_size} bytes)."
            )

    is_valid = len(errors) == 0
    return ValidationResult(
        is_valid, tuple(errors), tuple(warnings), discovered, metadata
    )


def validate_hwsd_dataset(input_path: Path | str) -> ValidationResult:
    """Automatically discover and validate raw HWSD dataset files.

    Args:
        input_path: Path to dataset directory or ZIP archive.

    Returns:
        ValidationResult mapping validation status, errors, and metadata.
    """
    path = Path(input_path)
    if not path.exists():
        return ValidationResult(
            is_valid=False,
            errors=(f"Input path '{path}' does not exist.",),
            warnings=(),
            discovered_paths={},
            metadata={},
        )

    if path.is_file() and zipfile.is_zipfile(path):
        return _validate_zip_archive(path)
    elif path.is_dir():
        return _validate_directory(path)
    else:
        return ValidationResult(
            is_valid=False,
            errors=(f"Input path '{path}' is neither a directory nor a ZIP archive.",),
            warnings=(),
            discovered_paths={},
            metadata={},
        )


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
    result = validate_hwsd_dataset(config.raw_data_dir)
    if not result.is_valid:
        for err in result.errors:
            logger.error(err)
        raise ValueError(f"Dataset validation failed: {result.errors[0]}")
    else:
        logger.info("Validation checks completed successfully.")
        logger.info("Discovered paths: %s", result.discovered_paths)
        logger.info("Parsed metadata: %s", result.metadata)
