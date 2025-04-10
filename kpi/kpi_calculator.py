# kpi/kpi_calculator.py
from abc import ABC, abstractmethod
from typing import Any, Dict

class KpiCalculator(ABC):
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def group(self) -> str:
        pass

    @abstractmethod
    def calculate(self, data: Dict[str, Any]) -> Any:
        pass