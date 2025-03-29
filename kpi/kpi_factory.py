from kpi.yaw_calculator import YawCalculator
from kpi.pitch_calculator import PitchCalculator
from kpi.roll_calculator import RollCalculator
from kpi.yawn_calculator import YawnCalculator
from kpi.eyelid_openness_calculator import EyelidOpennessCalculator
from kpi.adult_calculator import AdultCalculator
from kpi.belt_calculator import BeltCalculator
from kpi.inattention_calculator import InattentionCalculator
from kpi.fatigue_calculator import FatigueCalculator
from kpi.sleep_calculator import SleepCalculator
from kpi.unresponsive_calculator import UnresponsiveCalculator
from kpi.drowsiness_calculator import DrowsinessCalculator
import logging

class KpiFactory:
    def __init__(self, config: dict):
        self.config = config
        logging.debug(f"KpiFactory initialized with config: {self.config}")
    
    def create_calculators(self):
        calculators = []
        enabled_kpis = [kpi["name"] for kpi in self.config.get("kpis", []) if kpi.get("enabled", True)]
        for kpi in enabled_kpis:
            key = kpi.lower()
            if key == "yaw":
                calculators.append(YawCalculator())
            elif key == "pitch":
                calculators.append(PitchCalculator())
            elif key == "roll":
                calculators.append(RollCalculator())
            elif key == "yawn":
                calculators.append(YawnCalculator())
            elif key in ["left_eye_openness", "right_eye_openness"]:
                if not any(isinstance(c, EyelidOpennessCalculator) for c in calculators):
                    calculators.append(EyelidOpennessCalculator())
            elif key == "adult":
                calculators.append(AdultCalculator())
            elif key == "belt":
                calculators.append(BeltCalculator())
            elif key == "inattention":
                calculators.append(InattentionCalculator())
            elif key == "fatigue":
                calculators.append(FatigueCalculator())
            elif key in ["microsleep", "sleep"]:
                if not any(isinstance(c, SleepCalculator) for c in calculators):
                    calculators.append(SleepCalculator())
            elif key == "unresponsive":
                calculators.append(UnresponsiveCalculator())
            elif key == "drowsiness":
                calculators.append(DrowsinessCalculator())
        logging.debug(f"Calculators created: {[calc.name() for calc in calculators]}")
        return calculators