# kpi/kpi_calculator.py
import logging

class KpiCalculator:
    def name(self) -> str:
        raise NotImplementedError("Subclasses must implement name()")
    
    def calculate(self, landmarks, image_size, frame=None):
        raise NotImplementedError("Subclasses must implement calculate()")