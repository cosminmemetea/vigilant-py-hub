# kpi/blink_rate_calculator.py
from kpi.kpi_calculator import KpiCalculator
import logging
from typing import Dict, Any

class BlinkRateCalculator(KpiCalculator):
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.threshold = self.config.get("threshold", 0.2)  # EAR threshold for blink
        self.blink_count = 0
        self.prev_openness = None

    def name(self) -> str:
        return "blink_rate"

    def group(self) -> str:
        return "numeric"

    def calculate(self, data: Dict[str, Any]) -> float:
        landmarks = data.get("landmarks")
        if not landmarks:
            return 0.0
        
        # Simple EAR calculation (reuse logic from EyelidOpennessCalculator)
        left_eye_points = [landmarks.landmark[i] for i in [33, 159, 145, 133]]
        img_w, img_h = data["image_size"]
        coords = [(int(p.x * img_w), int(p.y * img_h)) for p in left_eye_points]
        vert_dist = ((coords[1][0] - coords[2][0])**2 + (coords[1][1] - coords[2][1])**2)**0.5
        hor_dist = ((coords[0][0] - coords[3][0])**2 + (coords[0][1] - coords[3][1])**2)**0.5
        ear = vert_dist / (hor_dist + 1e-6)

        if self.prev_openness is not None and self.prev_openness > self.threshold and ear <= self.threshold:
            self.blink_count += 1
        self.prev_openness = ear
        logging.debug(f"Blink count: {self.blink_count}")
        return self.blink_count  # Per frame, simplistic for now