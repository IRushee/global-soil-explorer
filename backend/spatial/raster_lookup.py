"""Spatial lookup implementation for ENVI flat binary rasters (BIL)."""

import struct
import threading
from pathlib import Path

from backend.contracts.spatial_lookup import SpatialLookupService
from backend.domain import Coordinate

MIN_LATITUDE = -90.0
MAX_LATITUDE = 90.0
MIN_LONGITUDE = -180.0
MAX_LONGITUDE = 180.0
BYTES_PER_PIXEL = 2
MIN_PARTS_COUNT = 2


class BILRasterSpatialLookupService(SpatialLookupService[int | None]):
    """Resolves geographic coordinates to mapping units using a BIL raster."""

    def __init__(self, bil_path: Path | str, hdr_path: Path | str) -> None:
        """Initialize lookup service and parse raster header metadata.

        Args:
            bil_path: Path to the flat binary .bil spatial grid.
            hdr_path: Path to the .hdr metadata header.
        """
        self._bil_path = Path(bil_path)
        self._hdr_path = Path(hdr_path)

        if not self._bil_path.exists():
            raise FileNotFoundError(f"Raster file not found: {self._bil_path}")
        if not self._hdr_path.exists():
            raise FileNotFoundError(f"Header file not found: {self._hdr_path}")

        # Parse header metadata
        metadata = self._parse_hdr(self._hdr_path)
        self._ncols = int(metadata.get("ncols", 43200))
        self._nrows = int(metadata.get("nrows", 21600))
        self._xdim = float(metadata.get("xdim", 0.00833333333333333))
        self._ydim = float(metadata.get("ydim", 0.00833333333333333))
        self._nodata = int(metadata.get("nodata", 65535))

        # Calculate grid boundaries
        self._min_lon = float(
            metadata.get("ulxmap", -179.995833333333)
        ) - (self._xdim / 2.0)
        self._max_lat = float(
            metadata.get("ulymap", 89.9958333333333)
        ) + (self._ydim / 2.0)

        # Open file handle and initialize mutex for thread-safe concurrent reads
        self._file = open(self._bil_path, "rb")
        self._lock = threading.Lock()

    def _parse_hdr(self, hdr_path: Path) -> dict[str, str]:
        """Parse key-value pairs from ENVI header file."""
        metadata = {}
        with open(hdr_path, encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                parts = stripped.replace("=", " ").split()
                if len(parts) >= MIN_PARTS_COUNT:
                    metadata[parts[0].lower()] = parts[1]
        return metadata

    def resolve(self, coordinate: Coordinate) -> int | None:
        """Resolve a geographic coordinate into a mapping unit identifier (SMU_ID).

        Args:
            coordinate: The geographic Coordinate to resolve.

        Returns:
            The mapping unit identifier, or None if ocean/NoData/out-of-bounds.
        """
        lat = coordinate.latitude
        lon = coordinate.longitude

        # 1. Bounds verification
        if (
            lat < MIN_LATITUDE
            or lat > MAX_LATITUDE
            or lon < MIN_LONGITUDE
            or lon > MAX_LONGITUDE
        ):
            return None

        # 2. Grid cell index calculation
        col = int((lon - self._min_lon) / self._xdim)
        row = int((self._max_lat - lat) / self._ydim)

        # Clamp right/bottom boundaries
        if lon == MAX_LONGITUDE:
            col = self._ncols - 1
        if lat == MIN_LATITUDE:
            row = self._nrows - 1

        # 3. Off-grid index check
        if col < 0 or col >= self._ncols or row < 0 or row >= self._nrows:
            return None

        # 4. Binary offset query (2 bytes per pixel for unsigned 16-bit)
        byte_offset = (row * self._ncols + col) * BYTES_PER_PIXEL

        with self._lock:
            self._file.seek(byte_offset)
            data = self._file.read(BYTES_PER_PIXEL)

        if len(data) < BYTES_PER_PIXEL:
            return None

        val = int(struct.unpack("<H", data)[0])

        # 5. Ocean/NoData filtering
        if val in (self._nodata, 0):
            return None

        return val

    def close(self) -> None:
        """Close the open file descriptor."""
        with self._lock:
            if not self._file.closed:
                self._file.close()

    def __del__(self) -> None:
        """Destructor to ensure resources are cleaned up."""
        try:
            self.close()
        except Exception:
            pass
