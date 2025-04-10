# processors/frame_processor.py
import cv2
import logging
from typing import Dict, Any

class FrameProcessor:
    def __init__(self, mediapipe_adapter, kpi_manager):
        self.mediapipe_adapter = mediapipe_adapter
        self.kpi_manager = kpi_manager
        logging.debug(f"FrameProcessor initialized with calculators: {[calc.name() for calc in self.kpi_manager.calculators]}")

    def process_frame(self, frame) -> Dict[str, Any]:
        logging.debug(f"Processing frame: {frame.shape}")
        results = {}
        processed_landmarks = self.mediapipe_adapter.process(frame)
        data = {
            "landmarks": processed_landmarks.multi_face_landmarks[0] if processed_landmarks and processed_landmarks.multi_face_landmarks else None,
            "image_size": (frame.shape[1], frame.shape[0]),
            "frame": frame
        }
        return self.kpi_manager.calculate(data)