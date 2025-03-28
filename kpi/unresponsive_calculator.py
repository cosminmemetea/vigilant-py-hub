from kpi.kpi_calculator import KpiCalculator
from kpi.eyelid_openness_calculator import EyelidOpennessCalculator
import logging
import time

_eyelid_calculator = EyelidOpennessCalculator()

class UnresponsiveCalculator(KpiCalculator):
    def __init__(self, fps=30):
        self.fps = fps
        self.warning_threshold = 3.0  # 3s after distraction warning
        self.eye_closure_threshold = 6.0  # ≥6s eye closure
        
        self.eye_closed_start_time = None
        self.eye_closure_duration = 0.0
        self.distraction_warning_time = None
        self.unresponsive_status = "None"
        self.last_gaze_state = "Center"  # Track gaze state internally
        self.gaze_state_start_time = time.time()
        logging.debug("UnresponsiveCalculator initialized.")

    def name(self) -> str:
        return "unresponsive"

    def calculate(self, landmarks, image_size, frame=None) -> str:
        if not landmarks:
            logging.warning("Unresponsive: No landmarks provided.")
            self._reset_state()
            return "None"
        
        current_time = time.time()

        # Get eye openness (EAR)
        eye_results = _eyelid_calculator.calculate(landmarks, image_size, frame)
        left_ear = eye_results.get("left_eye_openness", 0.0)
        right_ear = eye_results.get("right_eye_openness", 0.0)
        avg_ear = (left_ear + right_ear) / 2
        eye_closure_threshold = 0.2
        
        # Check eye closure duration
        if avg_ear < eye_closure_threshold:
            if self.eye_closed_start_time is None:
                self.eye_closed_start_time = current_time
                logging.debug(f"Eye closure started: EAR={avg_ear:.2f}")
            self.eye_closure_duration = current_time - self.eye_closed_start_time
            if self.eye_closure_duration >= self.eye_closure_threshold:
                self.unresponsive_status = "Detected (Eyes)"
                logging.debug(f"Unresponsive detected: Eyes closed for {self.eye_closure_duration:.2f}s")
                return self.unresponsive_status
        else:
            if self.eye_closed_start_time is not None:
                logging.debug(f"Eyes opened: Duration={self.eye_closure_duration:.2f}s")
                self.eye_closed_start_time = None
                self.eye_closure_duration = 0.0

        # Calculate gaze direction (simplified from LizardLookingCalculator)
        img_w, img_h = image_size
        left_eye_center = landmarks.landmark[468]
        right_eye_center = landmarks.landmark[473]
        left_eye_center_x = int(left_eye_center.x * img_w)
        right_eye_center_x = int(right_eye_center.x * img_w)
        left_eye_center_y = int(left_eye_center.y * img_h)
        right_eye_center_y = int(right_eye_center.y * img_h)
        
        frame_center_x = img_w / 2
        frame_center_y = img_h / 2
        avg_x = (left_eye_center_x + right_eye_center_x) / 2
        avg_y = (left_eye_center_y + right_eye_center_y) / 2
        x_offset = (avg_x - frame_center_x) / (img_w * 0.5)
        y_offset = (avg_y - frame_center_y) / (img_h * 0.5)
        
        center_threshold = 0.2
        directional_threshold = 0.3
        
        current_gaze_state = "Center"
        if abs(x_offset) <= center_threshold and abs(y_offset) <= center_threshold:
            current_gaze_state = "Center"
        elif x_offset > directional_threshold or x_offset < -directional_threshold or \
             y_offset > directional_threshold or y_offset < -directional_threshold:
            current_gaze_state = "Off-Center"

        # Update gaze state
        if current_gaze_state != self.last_gaze_state:
            self.gaze_state_start_time = current_time
            self.last_gaze_state = current_gaze_state
            logging.debug(f"Gaze state changed to: {current_gaze_state}")

        # Check for distraction warning (simplified: any off-center gaze triggers warning)
        if current_gaze_state != "Center":
            if self.distraction_warning_time is None:
                self.distraction_warning_time = current_time
                logging.debug(f"Distraction warning issued at {current_time}")
        
        # Check unresponsive due to gaze
        if self.distraction_warning_time is not None:
            time_since_warning = current_time - self.distraction_warning_time
            if time_since_warning >= self.warning_threshold and current_gaze_state != "Center":
                self.unresponsive_status = "Detected (Gaze)"
                logging.debug(f"Unresponsive detected: Gaze not returned after {time_since_warning:.2f}s")
                return self.unresponsive_status
            elif current_gaze_state == "Center":
                logging.debug(f"Gaze returned to Center, resetting warning")
                self.distraction_warning_time = None
        
        self.unresponsive_status = "None"
        return self.unresponsive_status

    def _reset_state(self):
        self.eye_closed_start_time = None
        self.eye_closure_duration = 0.0
        self.distraction_warning_time = None
        self.unresponsive_status = "None"
        self.last_gaze_state = "Center"
        self.gaze_state_start_time = time.time()