from kpi.kpi_calculator import KpiCalculator
from kpi.head_pose_estimator import HeadPoseEstimator
import logging
from typing import Dict, Any

class PitchCalculator(KpiCalculator):
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.estimator = HeadPoseEstimator()
        self.threshold = self.config.get("threshold", 20.0)

    def name(self) -> str:
        return "pitch"

    def group(self) -> str:
        return "numeric"

    def calculate(self, data: Dict[str, Any]) -> float:
        landmarks = data.get("landmarks")
        image_size = data.get("image_size")
        if not landmarks:
            return 0.0
        pose = self.estimator.estimate(landmarks, image_size)
        pitch = pose["pitch"] if pose else 0.0
        logging.debug(f"Pitch calculated: {pitch}, threshold: {self.threshold}")
        return pitch