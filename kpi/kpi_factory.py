# kpi/kpi_factory.py (updated)
from kpi.sleep_calculator import SleepCalculator
from kpi.unresponsive_calculator import UnresponsiveCalculator
from kpi.yaw_calculator import YawCalculator
from kpi.pitch_calculator import PitchCalculator
from kpi.roll_calculator import RollCalculator
from kpi.tilt_calculator import TiltCalculator
from kpi.yawn_calculator import YawnCalculator
from kpi.owl_looking_calculator import OwlLookingCalculator
from kpi.lizard_looking_calculator import LizardLookingCalculator
from kpi.eyelid_openness_calculator import EyelidOpennessCalculator
from kpi.adult_calculator import AdultCalculator
from kpi.belt_calculator import BeltCalculator
from kpi.distraction_calculator import DistractionCalculator
from kpi.inattention_calculator import InattentionCalculator  # New
from kpi.fatigue_calculator import FatigueCalculator  # New
import logging

class KpiFactory:
    def __init__(self, config: dict):
        self.config = config
        logging.debug(f"KpiFactory initialized with config: {self.config}")
    
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
            elif key == "owl_looking":
                calculators.append(OwlLookingCalculator())
            elif key == "lizard_looking":
                calculators.append(LizardLookingCalculator())
            elif key == "eyelid_openness":
                calculators.append(EyelidOpennessCalculator())
            elif key == "adult":
                calculators.append(AdultCalculator())
            elif key == "belt":
                calculators.append(BeltCalculator())
            elif key == "distraction":
                calculators.append(DistractionCalculator())
            elif key == "inattention":  # New
                calculators.append(InattentionCalculator())
            elif key == "fatigue":  # New
                calculators.append(FatigueCalculator())
            elif key == "sleep":
                calculators.append(SleepCalculator())
            elif key == "unresponsive":
                calculators.append(UnresponsiveCalculator())
        logging.debug(f"Calculators created: {[calc.name() for calc in calculators]}")
        return calculators