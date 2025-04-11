from kpi.kpi_calculator import KpiCalculator
import numpy as np
import logging
from typing import Dict, Any

class YawnCalculator(KpiCalculator):
    def __init__(self, config: Dict = None):
        self.config = config or {}
        # NCAP-inspired threshold: mouth opening > 0.5 (normalized) ≈ yawn
        self.openness_threshold = self.config.get("openness_threshold", 0.5)
        # MediaPipe landmarks: upper lip (13), lower lip (14), left corner (61), right corner (291)
        self.mouth_indices = [13, 14, 61, 291]

    def name(self) -> str:
        return "yawn"

    def group(self) -> str:
        return "state"  # Binary state for NCAP drowsiness

    def calculate(self, data: Dict[str, Any]) -> str:
        landmarks = data.get("landmarks")
        image_size = data.get("image_size")
        if not landmarks or not image_size:
            logging.debug("Yawn: No landmarks or image size provided.")
            return "None"
        
        img_w, img_h = image_size
        points = [landmarks.landmark[i] for i in self.mouth_indices]
        coords = [(int(p.x * img_w), int(p.y * img_h)) for p in points]
        
        # Vertical distance (upper to lower lip)
        vert_dist = np.linalg.norm(np.array(coords[0]) - np.array(coords[1]))
        # Horizontal distance (left to right corner)
        hor_dist = np.linalg.norm(np.array(coords[2]) - np.array(coords[3]))
        # Normalized openness (EAR-like metric)
        openness = vert_dist / (hor_dist + 1e-6)
        
        result = "Detected" if openness >= self.openness_threshold else "None"
        logging.debug(f"Yawn: openness={openness:.2f}, result={result}")
        return result