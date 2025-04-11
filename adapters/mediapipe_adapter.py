# adapters/mediapipe_adapter.py
# Defines the MediaPipeAdapter class, an interface for processing frames with MediaPipe's FaceMesh.

import mediapipe as mp  # MediaPipe library for facial landmark detection.
import cv2  # OpenCV library for image processing and color conversion.
import logging  # Facilitates logging for debugging and monitoring frame processing.

class MediaPipeAdapter:
    def __init__(self, mode="live", config=None):
        """Initialize the MediaPipeAdapter with FaceMesh configuration.

        Args:
            mode: Processing mode ('live' or 'static'), currently unused but reserved for future use.
            config: Dictionary of configuration options for FaceMesh (optional).
        """
        self.config = config or {}  # Use empty dict if no config provided.
        # Initialize MediaPipe FaceMesh with configuration options or defaults.
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=self.config.get("max_num_faces", 1),  # Max faces to detect.
            refine_landmarks=self.config.get("refine_landmarks", True),  # Refine facial landmarks.
            min_detection_confidence=self.config.get("min_detection_confidence", 0.5),  # Detection confidence threshold.
            min_tracking_confidence=self.config.get("min_tracking_confidence", 0.5)  # Tracking confidence threshold.
        )
        logging.debug(f"MediaPipeAdapter initialized with mode: {mode}, config: {self.config}")

    def process(self, frame):
        """Process a frame to detect facial landmarks using MediaPipe FaceMesh.

        Args:
            frame: Input frame (numpy array) in BGR format from OpenCV.

        Returns:
            mediapipe.python.solutions.face_mesh.FaceMeshResults: Results containing detected landmarks.
        """
        # Convert frame from BGR (OpenCV) to RGB (MediaPipe requirement).
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        logging.debug("Processing image with MediaPipe...")
        
        # Process the frame to detect facial landmarks.
        results = self.face_mesh.process(rgb_frame)
        if results.multi_face_landmarks:
            # Log number of detected faces and landmarks for the first face.
            logging.debug(f"Detected {len(results.multi_face_landmarks)} faces")
            logging.debug(f"Landmarks detected: {len(results.multi_face_landmarks[0].landmark)} landmarks")
        else:
            logging.warning("No faces detected.")
        
        return results

    def __del__(self):
        """Clean up resources by closing the FaceMesh instance."""
        self.face_mesh.close()  # Release MediaPipe resources.