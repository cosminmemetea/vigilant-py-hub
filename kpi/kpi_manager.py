# kpi/kpi_manager.py
# Defines the KpiManager class, responsible for managing and executing KPI calculators.

import logging  # Facilitates logging for debugging and monitoring calculator execution.
from typing import Dict, Any  # Type hints for flexible dictionary inputs and outputs.

class KpiManager:
    def __init__(self):
        """Initialize the KpiManager with an empty list of calculators."""
        self.calculators = []  # Store registered KPI calculators.
        logging.debug("KpiManager initialized.")

    def register_calculator(self, calculator):
        """Register a KPI calculator for execution.

        Args:
            calculator: A KpiCalculator instance to be added to the manager.
        """
        self.calculators.append(calculator)  # Add calculator to the list.
        logging.debug(f"Calculator registered: {calculator.name()}")

    def calculate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute all registered calculators on the input data.

        Args:
            data: Dictionary containing processed frame data (e.g., landmarks, image size).

        Returns:
            Dict[str, Any]: Dictionary mapping calculator names to their results.
        """
        results = {}  # Initialize dictionary to store calculation results.
        for calculator in self.calculators:
            logging.debug(f"Executing calculator: {calculator.name()}")
            # Store each calculator's result under its name.
            results[calculator.name()] = calculator.calculate(data)
        return results