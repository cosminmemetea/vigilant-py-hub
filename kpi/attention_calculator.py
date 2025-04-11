from kpi.kpi_calculator import KpiCalculator
from kpi.head_pose_estimator import HeadPoseEstimator
import logging
import time
from typing import Dict, Any

class AttentionCalculator(KpiCalculator):
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.estimator = HeadPoseEstimator()
        # NCAP-inspired thresholds (Euro NCAP DMS protocols)
        self.yaw_threshold = self.config.get("yaw_threshold", 20.0)  # ±20° yaw for forward gaze
        self.pitch_threshold = self.config.get("pitch_threshold", 15.0)  # ±15° pitch for forward gaze
        self.eye_openness_threshold = self.config.get("eye_openness_threshold", 0.2)  # EAR < 0.2 ≈ closed eyes
        self.distraction_time_threshold = self.config.get("distraction_time_threshold", 2.0)  # 2 seconds per NCAP
        
        # State tracking
        self.last_state = "None"
        self.distraction_start_time = None
        self.drowsiness_detected = False

    def name(self) -> str:
        return "attention"

    def group(self) -> str:
        return "state"  # Fits NCAP’s safety state reporting

    def calculate(self, data: Dict[str, Any]) -> str:
        landmarks = data.get("landmarks")
        image_size = data.get("image_size")
        if not landmarks:
            self.reset_tracking()
            return "None"
        
        # Head pose analysis
        pose = self.estimator.estimate(landmarks, image_size)
        if not pose:
            self.reset_tracking()
            return "None"
        
        yaw = abs(pose["yaw"])
        pitch = abs(pose["pitch"])
        gaze_forward = yaw <= self.yaw_threshold and pitch <= self.pitch_threshold

        # Eye openness analysis (requires left/right_eye_openness KPIs)
        left_eye_openness = data.get("left_eye_openness", 1.0)  # Default to open if missing
        right_eye_openness = data.get("right_eye_openness", 1.0)
        eyes_open = (left_eye_openness >= self.eye_openness_threshold and 
                     right_eye_openness >= self.eye_openness_threshold)

        # Determine current state
        current_time = time.time()
        if gaze_forward and eyes_open:
            state = "Attentive"
            self.reset_tracking()
        elif not eyes_open:
            state = "Drowsy"  # Eyes closed → potential drowsiness
            self.drowsiness_detected = True
            self.distraction_start_time = self.distraction_start_time or current_time
        else:
            state = "Distracted"  # Off-road gaze
            self.distraction_start_time = self.distraction_start_time or current_time

        # Check for sustained distraction/drowsiness
        if self.distraction_start_time and state != "Attentive":
            distraction_duration = current_time - self.distraction_start_time
            if distraction_duration >= self.distraction_time_threshold:
                state = f"{state} (> {self.distraction_time_threshold}s)"
        
        self.last_state = state
        logging.debug(f"Attention calculated: {state} (yaw={yaw:.2f}, pitch={pitch:.2f}, "
                      f"left_eye={left_eye_openness:.2f}, right_eye={right_eye_openness:.2f})")
        return state

    def reset_tracking(self):
        """Reset distraction tracking when attentive."""
        self.distraction_start_time = None
        self.drowsiness_detected = False