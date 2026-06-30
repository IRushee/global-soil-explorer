"""Abstraction for soil observation repositories."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from backend.domain import SoilObservation

T = TypeVar("T")


class SoilObservationRepository(ABC, Generic[T]):
    """Interface for retrieving validated SoilObservation objects."""

    @abstractmethod
    def get_by_key(self, key: T) -> SoilObservation:
        """Retrieve a fully constructed SoilObservation using a spatial key.

        Args:
            key: The dataset-specific spatial key.

        Returns:
            A fully constructed and validated SoilObservation object.
        """
        pass
