"""Abstraction for spatial lookup services."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from backend.domain import Coordinate

T = TypeVar("T")


class SpatialLookupService(ABC, Generic[T]):
    """Interface for resolving coordinates into spatial keys."""

    @abstractmethod
    def resolve(self, coordinate: Coordinate) -> T:
        """Resolve a geographic coordinate into a dataset-specific spatial key.

        Args:
            coordinate: The geographic Coordinate to resolve.

        Returns:
            The dataset-specific spatial key required by the repository.
        """
        pass
