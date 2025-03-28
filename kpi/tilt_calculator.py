# kpi/tilt_calculator.py
from kpi.kpi_calculator import KpiCalculator
import numpy as np
import math

class TiltCalculator(KpiCalculator):
    def name(self) -> str:
        return "tilt"
    
    def calculate(self, landmarks, image_size, frame=None) -> float:
        if not landmarks:
            return 0.0
        left_eye = landmarks.landmark[33]
        right_eye = landmarks.landmark[263]
        left = np.array([left_eye.x * image_size[0], left_eye.y * image_size[1]])
        right = np.array([right_eye.x * image_size[0], right_eye.y * image_size[1]])
        delta_y = right[1] - left[1]
        delta_x = right[0] - left[0]
        angle = np.degrees(np.arctan2(delta_y, delta_x))
        return angle