# adapters/mediapipe_adapter.py
import mediapipe as mp
import cv2
import logging

class MediaPipeAdapter:
    def __init__(self, mode="live", config=None):
        self.config = config or {}
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=self.config.get("max_num_faces", 1),
            refine_landmarks=self.config.get("refine_landmarks", True),
            min_detection_confidence=self.config.get("min_detection_confidence", 0.5),
            min_tracking_confidence=self.config.get("min_tracking_confidence", 0.5)
        )
        logging.debug(f"MediaPipeAdapter initialized with mode: {mode}, config: {self.config}")

    def process(self, frame):
        # Convert the frame to RGB as required by MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        logging.debug("Processing image with MediaPipe...")
        
        # Process the frame with FaceMesh
        results = self.face_mesh.process(rgb_frame)
        if results.multi_face_landmarks:
            logging.debug(f"Detected {len(results.multi_face_landmarks)} faces")
            logging.debug(f"Landmarks detected: {len(results.multi_face_landmarks[0].landmark)} landmarks")
        else:
            logging.warning("No faces detected.")
        
        return results

    def __del__(self):
        self.face_mesh.close()