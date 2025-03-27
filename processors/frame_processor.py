# processors/frame_processor.py
import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)

class FrameProcessor:
    def __init__(self, mediapipe_adapter, kpi_manager):
        self.mediapipe_adapter = mediapipe_adapter
        self.kpi_manager = kpi_manager

    def process_frame(self, frame: np.ndarray) -> dict:
        try:
            print("Starting frame processing...")
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image_size = (frame.shape[1], frame.shape[0])
            landmarks = self.mediapipe_adapter.process(rgb_frame)
            if landmarks is not None:
                print(f"Landmarks detected: {len(landmarks.landmark)} landmarks")
                results = self.kpi_manager.calculate_all(landmarks, image_size)
                print(f"Processed frame results: {results}")
                return results
            else:
                print("No landmarks detected in frame")
                return {}
        except Exception as e:
            print(f"Error processing frame: {e}")
            return {}