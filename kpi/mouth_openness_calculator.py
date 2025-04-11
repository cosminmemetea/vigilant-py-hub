from kpi.kpi_calculator import KpiCalculator
import numpy as np
import logging
from typing import Dict, Any

class MouthOpennessCalculator(KpiCalculator):
    def __init__(self, config: Dict = None):
        self.config = config or {}
        # No threshold here—raw value for flexibility (e.g., NCAP analysis)
        # MediaPipe landmarks: upper lip (13), lower lip (14), left corner (61), right corner (291)
        self.mouth_indices = [13, 14, 61, 291]

    def name(self) -> str:
        return "mouth_openness"

    def group(self) -> str:
        return "numeric"  # Continuous value for NCAP drowsiness precursor

    def calculate(self, data: Dict[str, Any]) -> float:
        landmarks = data.get("landmarks")
        image_size = data.get("image_size")
        if not landmarks or not image_size:
            logging.debug("MouthOpenness: No landmarks or image size provided.")
            return 0.0
        
        img_w, img_h = image_size
        points = [landmarks.landmark[i] for i in self.mouth_indices]
        coords = [(int(p.x * img_w), int(p.y * img_h)) for p in points]
        
        # Vertical distance (upper to lower lip)
        vert_dist = np.linalg.norm(np.array(coords[0]) - np.array(coords[1]))
        # Horizontal distance (left to right corner)
        hor_dist = np.linalg.norm(np.array(coords[2]) - np.array(coords[3]))
        # Normalized openness
        openness = vert_dist / (hor_dist + 1e-6)
        
        logging.debug(f"Mouth Openness: openness={openness:.2f}")
        return openness