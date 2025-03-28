from kpi.kpi_calculator import KpiCalculator
from kpi.eyelid_openness_calculator import EyelidOpennessCalculator
import logging
import time

_eyelid_calculator = EyelidOpennessCalculator()

class SleepCalculator(KpiCalculator):
    def __init__(self, fps=30):
        self.fps = fps
        self.microsleep_min = 1.0  # Microsleep: 1-2s eye closure
        self.microsleep_max = 2.0
        self.sleep_threshold = 3.0  # Sleep: ≥3s eye closure
        
        self.eye_closed_start_time = None
        self.eye_closure_duration = 0.0
        self.microsleep_status = "None"  # Separate KPI for Microsleep
        self.sleep_status = "None"      # Separate KPI for Sleep
        logging.debug("SleepCalculator initialized.")

    def name(self) -> str:
        return "sleep"

    def calculate(self, landmarks, image_size, frame=None) -> dict:
        if not landmarks:
            logging.warning("Sleep: No landmarks provided.")
            self._reset_state()
            return {"microsleep": "None", "sleep": "None"}
        
        # Calculate EAR using EyelidOpennessCalculator
        eye_results = _eyelid_calculator.calculate(landmarks, image_size, frame)
        left_ear = eye_results.get("left_eye_openness", 0.0)
        right_ear = eye_results.get("right_eye_openness", 0.0)
        avg_ear = (left_ear + right_ear) / 2
        eye_closure_threshold = 0.2  # EAR threshold for closed eyes
        
        current_time = time.time()
        
        # Check eye closure duration
        if avg_ear < eye_closure_threshold:
            if self.eye_closed_start_time is None:
                self.eye_closed_start_time = current_time
                logging.debug(f"Eye closure started: EAR={avg_ear:.2f}")
            self.eye_closure_duration = current_time - self.eye_closed_start_time
            
            # Microsleep: 1-2s closure
            if self.microsleep_min <= self.eye_closure_duration <= self.microsleep_max:
                self.microsleep_status = "Detected"
                self.sleep_status = "None"
                logging.debug(f"Microsleep detected: {self.eye_closure_duration:.2f}s closure")
            # Sleep: ≥3s closure
            elif self.eye_closure_duration >= self.sleep_threshold:
                self.microsleep_status = "None"
                self.sleep_status = "Detected"
                logging.debug(f"Sleep detected: {self.eye_closure_duration:.2f}s closure")
            else:
                self.microsleep_status = "Pending"
                self.sleep_status = "None"
        else:
            if self.eye_closed_start_time is not None:
                logging.debug(f"Eyes opened: Duration={self.eye_closure_duration:.2f}s")
                self.eye_closed_start_time = None
                self.eye_closure_duration = 0.0
            self.microsleep_status = "None"
            self.sleep_status = "None"
        
        logging.debug(f"Sleep - EAR: {avg_ear:.2f}, Microsleep: {self.microsleep_status}, Sleep: {self.sleep_status}")
        return {"microsleep": self.microsleep_status, "sleep": self.sleep_status}

    def _reset_state(self):
        self.eye_closed_start_time = None
        self.eye_closure_duration = 0.0
        self.microsleep_status = "None"
        self.sleep_status = "None"