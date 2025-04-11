from kpi.kpi_calculator import KpiCalculator
import numpy as np
import logging
from typing import Dict, Any

class LeftEyeOpennessCalculator(KpiCalculator):
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.threshold = self.config.get("threshold", 0.3)  # NCAP-like threshold for "open"
        # MediaPipe refined landmark indices for left eye
        self.eye_indices = [33, 159, 145, 133]  # Outer, upper, lower, inner

    def name(self) -> str:
        return "left_eye_openness"

    def group(self) -> str:
        return "numeric"

    def calculate(self, data: Dict[str, Any]) -> float:
        landmarks = data.get("landmarks")
        image_size = data.get("image_size")
        if not landmarks or not image_size:
            logging.debug("LeftEyeOpenness: No landmarks or image size provided.")
            return 0.0
        
        img_w, img_h = image_size
        points = [landmarks.landmark[i] for i in self.eye_indices]
        coords = [(int(p.x * img_w), int(p.y * img_h)) for p in points]
        
        # EAR: vertical distance (upper to lower) / horizontal distance (outer to inner)
        vert_dist = np.linalg.norm(np.array(coords[1]) - np.array(coords[2]))
        hor_dist = np.linalg.norm(np.array(coords[0]) - np.array(coords[3]))
        ear = vert_dist / (hor_dist + 1e-6)  # Avoid division by zero
        
        logging.debug(f"Left Eye Openness: EAR={ear:.2f}")
        return ear