from kpi.kpi_calculator import KpiCalculator
from kpi.eyelid_openness_calculator import EyelidOpennessCalculator
from kpi.yawn_calculator import YawnCalculator
from kpi.owl_looking_calculator import OwlLookingCalculator
import logging
import time
from collections import deque

_eyelid_calculator = EyelidOpennessCalculator()
_yawn_calculator = YawnCalculator()
_owl_calculator = OwlLookingCalculator()

class DrowsinessCalculator(KpiCalculator):
    def __init__(self, fps=30):
        self.fps = fps
        self.min_speed = 50  # Minimum speed (km/h) for drowsiness detection (placeholder)
        self.drowsiness_threshold = 7.0  # Equivalent to KSS ≥ 7
        self.window_duration = 60.0  # 60s sliding window for metrics
        
        # Tracking variables
        self.eye_closure_events = deque()  # (timestamp, duration)
        self.yawn_events = deque()        # (timestamp)
        self.head_deviation_sum = 0.0     # Sum of head deviation over window
        self.drowsiness_score = 0.0
        self.drowsiness_status = "None"
        self.last_update_time = time.time()
        logging.debug("DrowsinessCalculator initialized.")

    def name(self) -> str:
        return "drowsiness"

    def calculate(self, landmarks, image_size, frame=None) -> str:
        if not landmarks:
            logging.warning("Drowsiness: No landmarks provided.")
            self._reset_state()
            return "None"
        
        current_time = time.time()

        # Placeholder for speed check (assuming always active for now)
        speed = 50  # Replace with actual speed input if available
        
        if speed < self.min_speed:
            self.drowsiness_status = "Inactive (Speed < 50 km/h)"
            return self.drowsiness_status

        # Eye closure (EAR)
        eye_results = _eyelid_calculator.calculate(landmarks, image_size, frame)
        avg_ear = (eye_results.get("left_eye_openness", 0.0) + eye_results.get("right_eye_openness", 0.0)) / 2
        eye_closure_threshold = 0.2
        
        if avg_ear < eye_closure_threshold:
            if not hasattr(self, 'eye_closure_start') or self.eye_closure_start is None:
                self.eye_closure_start = current_time
                logging.debug(f"Eye closure started: EAR={avg_ear:.2f}")
        else:
            if hasattr(self, 'eye_closure_start') and self.eye_closure_start is not None:
                duration = current_time - self.eye_closure_start
                self.eye_closure_events.append((current_time, duration))
                logging.debug(f"Eye closure event: {duration:.2f}s")
                self.eye_closure_start = None

        # Yawn detection
        yawn_ratio = _yawn_calculator.calculate(landmarks, image_size, frame)
        yawn_threshold = 0.5
        if yawn_ratio > yawn_threshold:
            self.yawn_events.append(current_time)
            logging.debug(f"Yawn detected: Ratio={yawn_ratio:.2f}")

        # Head deviation
        owl_results = _owl_calculator.calculate(landmarks, image_size, frame)
        head_deviation = owl_results.get("deviation", 0.0)
        self.head_deviation_sum += head_deviation

        # Clean up events outside the 60s window
        while self.eye_closure_events and current_time - self.eye_closure_events[0][0] > self.window_duration:
            self.eye_closure_events.popleft()
        while self.yawn_events and current_time - self.yawn_events[0] > self.window_duration:
            self.yawn_events.popleft()

        # Calculate drowsiness score (heuristic based on KSS approximation)
        # Weights: Eye closure (0.5/s), Yawns (2/event), Head deviation (0.01/degree)
        eye_closure_total = sum(d for t, d in self.eye_closure_events)
        yawn_count = len(self.yawn_events)
        head_deviation_avg = self.head_deviation_sum / max(1, self.fps * (current_time - self.last_update_time))
        self.drowsiness_score = (0.5 * eye_closure_total) + (2.0 * yawn_count) + (0.01 * head_deviation_avg)
        
        # Reset head deviation sum periodically
        if current_time - self.last_update_time >= 1.0:  # Update every second
            self.head_deviation_sum = 0.0
            self.last_update_time = current_time

        # Determine drowsiness status
        if self.drowsiness_score >= self.drowsiness_threshold:
            self.drowsiness_status = "Detected"
            logging.debug(f"Drowsiness detected: Score={self.drowsiness_score:.2f}")
        else:
            self.drowsiness_status = "None"

        return self.drowsiness_status

    def _reset_state(self):
        self.eye_closure_events.clear()
        self.yawn_events.clear()
        self.head_deviation_sum = 0.0
        self.drowsiness_score = 0.0
        self.drowsiness_status = "None"
        self.last_update_time = time.time()
        if hasattr(self, 'eye_closure_start'):
            self.eye_closure_start = None