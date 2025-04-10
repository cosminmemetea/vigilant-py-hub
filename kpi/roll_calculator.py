from kpi.kpi_calculator import KpiCalculator
from kpi.head_pose_estimator import HeadPoseEstimator
import logging
from typing import Dict, Any

class RollCalculator(KpiCalculator):
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.estimator = HeadPoseEstimator()
        self.threshold = self.config.get("threshold", 25.0)

    def name(self) -> str:
        return "roll"

    def group(self) -> str:
        return "numeric"

    def calculate(self, data: Dict[str, Any]) -> float:
        landmarks = data.get("landmarks")
        image_size = data.get("image_size")
        if not landmarks:
            return 0.0
        pose = self.estimator.estimate(landmarks, image_size)
        roll = pose["roll"] if pose else 0.0
        logging.debug(f"Roll calculated: {roll}, threshold: {self.threshold}")
        return roll