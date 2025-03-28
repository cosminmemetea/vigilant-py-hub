# kpi/pitch_calculator.py
from kpi.kpi_calculator import KpiCalculator
from kpi.head_pose_estimator import HeadPoseEstimator

_head_pose_estimator = HeadPoseEstimator()

class PitchCalculator(KpiCalculator):
    def name(self) -> str:
        return "pitch"
    
    def calculate(self, landmarks, image_size, frame=None) -> float:
        head_pose = _head_pose_estimator.estimate(landmarks, image_size)
        return head_pose.get("pitch", 0.0) if head_pose else 0.0