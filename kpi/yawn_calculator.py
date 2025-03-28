# kpi/yawn_calculator.py
from kpi.kpi_calculator import KpiCalculator
import numpy as np

class YawnCalculator(KpiCalculator):
    def name(self) -> str:
        return "yawn"
    
    def calculate(self, landmarks, image_size, frame=None) -> float:
        if not landmarks:
            return 0.0
        top_lip = landmarks.landmark[13]
        bottom_lip = landmarks.landmark[14]
        left_mouth = landmarks.landmark[61]
        right_mouth = landmarks.landmark[291]
        
        top = np.array([top_lip.x * image_size[0], top_lip.y * image_size[1]])
        bottom = np.array([bottom_lip.x * image_size[0], bottom_lip.y * image_size[1]])
        left = np.array([left_mouth.x * image_size[0], left_mouth.y * image_size[1]])
        right = np.array([right_mouth.x * image_size[0], right_mouth.y * image_size[1]])
        
        vertical = np.linalg.norm(bottom - top)  # Fixed: should be 'bottom'
        horizontal = np.linalg.norm(right - left)
        return vertical / horizontal if horizontal != 0 else 0.0