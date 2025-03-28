# kpi/kpi_manager.py
import logging

class KpiManager:
    def __init__(self):
        self.calculators = []
        logging.debug("KpiManager initialized.")
    
    def register_calculator(self, calculator):
        self.calculators.append(calculator)
        logging.debug(f"Calculator registered: {calculator.name()}")
    
    def calculate(self, landmarks, image_size, frame):
        results = {}
        for calculator in self.calculators:
            logging.debug(f"Executing calculator: {calculator.name()}")
            result = calculator.calculate(landmarks, image_size, frame)
            if isinstance(result, dict):
                results.update(result)
            else:
                results[calculator.name()] = result
        return results