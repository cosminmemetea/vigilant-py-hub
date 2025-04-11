# kpi/kpi_calculator.py
# Defines the abstract KpiCalculator class, providing a blueprint for KPI calculation implementations.

from abc import ABC, abstractmethod  # Enables creation of abstract base classes with required methods.
from typing import Any, Dict  # Type hints for flexible dictionary inputs and calculation outputs.

class KpiCalculator(ABC):
    """Abstract base class for KPI calculators, defining the interface for metric computation."""

    @abstractmethod
    def name(self) -> str:
        """Return the unique name of the KPI.

        Returns:
            str: The identifier for this KPI (e.g., 'yaw', 'pitch').
        """
        pass

    @abstractmethod
    def group(self) -> str:
        """Return the group this KPI belongs to for UI organization.

        Returns:
            str: The group name (e.g., 'numeric', 'state').
        """
        pass

    @abstractmethod
    def calculate(self, data: Dict[str, Any]) -> Any:
        """Calculate the KPI value based on input data.

        Args:
            data: Dictionary containing processed frame data (e.g., landmarks, image size).

        Returns:
            Any: The calculated KPI value (e.g., float for numeric KPIs, bool for state KPIs).
        """
        pass