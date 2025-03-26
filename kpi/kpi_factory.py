# kpi/kpi_factory.py
from kpi.kpi_calculator import (YawCalculator, PitchCalculator, RollCalculator, 
                                TiltCalculator, YawnCalculator, AdultCalculator, BeltCalculator)

class KpiFactory:
    def __init__(self, config: dict):
        self.config = config

    def create_calculators(self):
        calculators = []
        for kpi in self.config.get("kpis", []):
            key = kpi.lower()
            if key == "yaw":
                calculators.append(YawCalculator())
            elif key == "pitch":
                calculators.append(PitchCalculator())
            elif key == "roll":
                calculators.append(RollCalculator())
            elif key == "tilt":
                calculators.append(TiltCalculator())
            elif key == "yawn":
                calculators.append(YawnCalculator())
            elif key == "adult":
                calculators.append(AdultCalculator())
            elif key == "belt":
                calculators.append(BeltCalculator())
        return calculators