# processors/frame_processor.py
# Defines the FrameProcessor class, responsible for processing video frames using MediaPipe and calculating KPIs.

import cv2  # OpenCV library for image and video processing.
import logging  # Enables logging for debugging and monitoring frame processing.
from typing import Dict, Any  # Type hints for flexible dictionary return types.

class FrameProcessor:
    def __init__(self, mediapipe_adapter, kpi_manager):
        """Initialize the FrameProcessor with a MediaPipe adapter and KPI manager.

        Args:
            mediapipe_adapter: Adapter for processing frames with MediaPipe.
            kpi_manager: Manager for calculating KPIs based on processed frame data.
        """
        self.mediapipe_adapter = mediapipe_adapter  # Store MediaPipe adapter for landmark detection.
        self.kpi_manager = kpi_manager  # Store KPI manager for metric calculations.
        # Log the initialized calculators for debugging.
        logging.debug(f"FrameProcessor initialized with calculators: {[calc.name() for calc in self.kpi_manager.calculators]}")

    def process_frame(self, frame) -> Dict[str, Any]:
        """Process a single video frame and calculate KPIs.

        Args:
            frame: Input frame (numpy array) from a video or camera feed.

        Returns:
            Dict[str, Any]: Dictionary containing KPI calculation results.
        """
        logging.debug(f"Processing frame: {frame.shape}")  # Log frame dimensions for debugging.
        results = {}  # Initialize empty results dictionary (to be populated by kpi_manager if needed).
        # Process the frame using MediaPipe to extract facial landmarks.
        processed_landmarks = self.mediapipe_adapter.process(frame)
        # Prepare data dictionary for KPI calculations.
        data = {
            # Extract first face's landmarks if available, otherwise None.
            "landmarks": processed_landmarks.multi_face_landmarks[0] if processed_landmarks and processed_landmarks.multi_face_landmarks else None,
            "image_size": (frame.shape[1], frame.shape[0]),  # Store frame width and height.
            "frame": frame  # Pass the original frame for potential use in calculations.
        }
        # Calculate KPIs using the prepared data and return results.
        return self.kpi_manager.calculate(data)