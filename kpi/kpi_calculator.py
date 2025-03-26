# kpi/kpi_calculator.py
from abc import ABC, abstractmethod
import numpy as np
from kpi.head_pose_estimator import HeadPoseEstimator
import math

class KpiCalculator(ABC):
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def calculate(self, landmarks, image_size) -> any:
        pass

_head_pose_estimator = HeadPoseEstimator()

class YawCalculator(KpiCalculator):
    def name(self) -> str:
        return "yaw"
    
    def calculate(self, landmarks, image_size) -> float:
        head_pose = _head_pose_estimator.estimate(landmarks, image_size)
        return head_pose.get("yaw", 0.0) if head_pose else 0.0

class PitchCalculator(KpiCalculator):
    def name(self) -> str:
        return "pitch"
    
    def calculate(self, landmarks, image_size) -> float:
        head_pose = _head_pose_estimator.estimate(landmarks, image_size)
        return head_pose.get("pitch", 0.0) if head_pose else 0.0

class RollCalculator(KpiCalculator):
    def name(self) -> str:
        return "roll"
    
    def calculate(self, landmarks, image_size) -> float:
        head_pose = _head_pose_estimator.estimate(landmarks, image_size)
        return head_pose.get("roll", 0.0) if head_pose else 0.0

class TiltCalculator(KpiCalculator):
    def name(self) -> str:
        return "tilt"
    
    def calculate(self, landmarks, image_size) -> float:
        left_eye = landmarks.landmark[33]
        right_eye = landmarks.landmark[263]
        left = np.array([left_eye.x * image_size[0], left_eye.y * image_size[1]])
        right = np.array([right_eye.x * image_size[0], right_eye.y * image_size[1]])
        delta_y = right[1] - left[1]
        delta_x = right[0] - left[0]
        angle = np.degrees(np.arctan2(delta_y, delta_x))
        return angle

class YawnCalculator(KpiCalculator):
    def name(self) -> str:
        return "yawn"
    
    def calculate(self, landmarks, image_size) -> float:
        top_lip = landmarks.landmark[13]
        bottom_lip = landmarks.landmark[14]
        left_mouth = landmarks.landmark[61]
        right_mouth = landmarks.landmark[291]
        
        top = np.array([top_lip.x * image_size[0], top_lip.y * image_size[1]])
        bottom = np.array([bottom_lip.x * image_size[0], bottom_lip.y * image_size[1]])
        left = np.array([left_mouth.x * image_size[0], left_mouth.y * image_size[1]])
        right = np.array([right_mouth.x * image_size[0], right_mouth.y * image_size[1]])
        
        vertical = np.linalg.norm(bottom - top)
        horizontal = np.linalg.norm(right - left)
        return vertical / horizontal if horizontal != 0 else 0.0

class AdultCalculator(KpiCalculator):
    def name(self) -> str:
        return "adult"
    
    def calculate(self, landmarks, image_size) -> str:
        return "1" if landmarks is not None else "Unknown"

class BeltCalculator(KpiCalculator):
    def name(self) -> str:
        return "belt"
    
    def calculate(self, landmarks, image_size) -> str:
        return "0"