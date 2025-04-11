# kpi/kpi_factory.py
# Defines the KpiFactory class, responsible for dynamically creating KPI calculator instances based on configuration.

import importlib  # Enables dynamic importing of modules for KPI calculators.
import logging  # Facilitates logging for debugging and error tracking.
from typing import List, Dict  # Type hints for lists and dictionaries.
from kpi.kpi_calculator import KpiCalculator  # Abstract base class for KPI calculators.

class KpiFactory:
    def __init__(self, config: Dict):
        """Initialize the KpiFactory with application configuration.

        Args:
            config: Dictionary containing KPI configurations (e.g., from config.json).
        """
        self.config = config  # Store the configuration for KPI creation.
        logging.debug(f"KpiFactory initialized with config: {self.config}")

    def create_calculators(self) -> List[KpiCalculator]:
        """Create a list of enabled KPI calculator instances based on configuration.

        Returns:
            List[KpiCalculator]: List of instantiated KPI calculators.
        """
        calculators = []  # Initialize empty list to store calculator instances.
        # Filter enabled KPIs from config and map by name for easy lookup.
        enabled_kpis = {
            kpi["name"]: kpi
            for kpi in self.config.get("kpis", [])
            if kpi.get("enabled", True)
        }

        for kpi_name in enabled_kpis:
            try:
                # Dynamically import the module for the KPI (e.g., kpi.yaw_calculator).
                module = importlib.import_module(f"kpi.{kpi_name}_calculator")

                # Construct the class name (e.g., YawCalculator from yaw_calculator).
                class_name = ''.join(part.capitalize() for part in kpi_name.split('_')) + "Calculator"
                calculator_class = getattr(module, class_name)

                # Instantiate the calculator with its specific parameters.
                calculators.append(
                    calculator_class(config=enabled_kpis[kpi_name].get("params", {}))
                )
                logging.debug(f"Loaded calculator: {kpi_name}")

            except (ImportError, AttributeError) as e:
                # Log errors if module or class cannot be loaded.
                logging.error(f"Failed to load calculator for '{kpi_name}': {e}")

        # Log the names of all successfully created calculators.
        logging.debug(f"Calculators created: {[calc.name() for calc in calculators]}")
        return calculators