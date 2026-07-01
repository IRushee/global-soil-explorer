"""Application service coordinating the runtime query pipeline."""

import logging
from typing import Any

from backend.application.exceptions import ApplicationServiceError
from backend.contracts.repository import SoilObservationRepository
from backend.contracts.spatial_lookup import SpatialLookupService
from backend.domain import Coordinate, SoilObservation
from backend.domain.exceptions import InvalidCoordinateError
from backend.domain.value_objects.coordinate import (
    MAX_LATITUDE,
    MAX_LONGITUDE,
    MIN_LATITUDE,
    MIN_LONGITUDE,
)

logger = logging.getLogger(__name__)


class ApplicationService:
    """Coordinating service that orchestrates spatial lookup and repository queries."""

    def __init__(
        self,
        spatial_lookup: SpatialLookupService[Any],
        repository: SoilObservationRepository[Any],
    ) -> None:
        """Initialize the application service with injected dependencies.

        Args:
            spatial_lookup: Injected spatial lookup service.
            repository: Injected soil observation repository.
        """
        self._spatial_lookup = spatial_lookup
        self._repository = repository

    def get_soil_observation(self, coordinate: Coordinate) -> SoilObservation | None:
        """Coordinate the query pipeline to get a soil observation for a coordinate.

        Args:
            coordinate: The validated geographic Coordinate.

        Returns:
            The SoilObservation if found, or None if no observation exists.

        Raises:
            InvalidCoordinateError: If the coordinate is outside valid bounds.
            ApplicationServiceError: For any underlying infrastructure failure.
        """
        # 1. Validate Coordinate bounds explicitly
        in_lat_bounds = MIN_LATITUDE <= coordinate.latitude <= MAX_LATITUDE
        in_lon_bounds = MIN_LONGITUDE <= coordinate.longitude <= MAX_LONGITUDE
        if not (in_lat_bounds and in_lon_bounds):
            raise InvalidCoordinateError(
                f"Coordinate outside valid geographic bounds: "
                f"lat={coordinate.latitude}, lon={coordinate.longitude}"
            )

        # 2. Invoke SpatialLookupService
        try:
            smu_id = self._spatial_lookup.resolve(coordinate)
        except Exception as e:
            logger.exception("Infrastructure failure in spatial lookup service.")
            raise ApplicationServiceError(
                "Spatial lookup failed due to infrastructure error."
            ) from e

        # 3. Handle "no mapping unit" results
        if smu_id is None:
            return None

        # 4. Invoke SoilObservationRepository
        try:
            obs = self._repository.get_by_key(smu_id)
        except KeyError:
            # Repository cannot find mapping unit
            return None
        except Exception as e:
            logger.exception("Infrastructure failure in soil observation repository.")
            raise ApplicationServiceError(
                "Database query failed due to infrastructure error."
            ) from e

        # 5. Return fully constructed/reconstructed SoilObservation
        try:
            return SoilObservation(coordinate=coordinate, profiles=obs.profiles)
        except Exception as e:
            logger.exception("Domain reconstruction failed.")
            raise ApplicationServiceError(
                "Failed to reconstruct soil observation domain object."
            ) from e
