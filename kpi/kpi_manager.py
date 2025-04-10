# kpi/kpi_manager.py
import logging
from typing import Dict, Any

class KpiManager:
    def __init__(self):
        self.calculators = []
        logging.debug("KpiManager initialized.")
    
    def register_calculator(self, calculator):
        self.calculators.append(calculator)
        logging.debug(f"Calculator registered: {calculator.name()}")
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        results = {}
        for calculator in self.calculators:
            logging.debug(f"Executing calculator: {calculator.name()}")
            results[calculator.name()] = calculator.calculate(data)
        return results