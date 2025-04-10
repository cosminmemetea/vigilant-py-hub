# kpi/kpi_factory.py
import importlib
import logging
from typing import List, Dict
from kpi.kpi_calculator import KpiCalculator

class KpiFactory:
    def __init__(self, config: Dict):
        self.config = config
        logging.debug(f"KpiFactory initialized with config: {self.config}")

    def create_calculators(self) -> List[KpiCalculator]:
        calculators = []
        enabled_kpis = {
            kpi["name"]: kpi
            for kpi in self.config.get("kpis", [])
            if kpi.get("enabled", True)
        }

        for kpi_name in enabled_kpis:
            try:
                # Import module dynamically: kpi/some_kpi_calculator.py
                module = importlib.import_module(f"kpi.{kpi_name}_calculator")

                # Assume the class is named like SomeKpiCalculator, matching module name
                class_name = ''.join(part.capitalize() for part in kpi_name.split('_')) + "Calculator"
                calculator_class = getattr(module, class_name)

                # Instantiate the calculator with its config
                calculators.append(
                    calculator_class(config=enabled_kpis[kpi_name].get("params", {}))
                )
                logging.debug(f"Loaded calculator: {kpi_name}")

            except (ImportError, AttributeError) as e:
                logging.error(f"Failed to load calculator for '{kpi_name}': {e}")

        logging.debug(f"Calculators created: {[calc.name() for calc in calculators]}")
        return calculators
