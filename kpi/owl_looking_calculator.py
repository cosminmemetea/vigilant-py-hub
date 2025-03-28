# kpi/owl_looking_calculator.py

from kpi.kpi_calculator import KpiCalculator
from kpi.head_pose_estimator import HeadPoseEstimator
import cv2
import math
import logging
import numpy as np

# Create a single instance of HeadPoseEstimator for this module.
_head_pose_estimator = HeadPoseEstimator()

class OwlLookingCalculator(KpiCalculator):
    def name(self) -> str:
        return "owl_looking"
    
    def calculate(self, landmarks, image_size, frame=None) -> dict:
        """
        Calculates head orientation numerically instead of returning qualitative strings.
        
        Returns a dictionary with:
          - 'yaw': the yaw angle in degrees,
          - 'pitch': the pitch angle in degrees,
          - 'deviation': the Euclidean distance from (0,0) computed as sqrt(yaw^2 + pitch^2).
        
        Optionally, if a frame is provided, the function will draw the nose tip and a direction
        vector on the frame to visualize the head pose.
        """
        # Check if landmarks are provided.
        if not landmarks:
            logging.warning("Owl: No landmarks provided.")
            return {"yaw": 0.0, "pitch": 0.0, "deviation": 0.0}
        
        # Estimate head pose from the landmarks.
        head_pose = _head_pose_estimator.estimate(landmarks, image_size)
        if not head_pose:
            logging.warning("Owl: Head pose estimation failed.")
            return {"yaw": 0.0, "pitch": 0.0, "deviation": 0.0}
        
        yaw = head_pose.get("yaw", 0.0)
        pitch = head_pose.get("pitch", 0.0)
        
        # Normalize pitch to the range [-180, 180].
        pitch = pitch % 360
        if pitch > 180:
            pitch -= 360
        
        # Debug logging for head pose values.
        logging.debug(f"Owl - Yaw: {yaw:.2f}, Pitch: {pitch:.2f}")
        
        # If a frame is provided, draw the visualization:
        # - A green circle at the nose tip (assumed landmark index 1).
        # - A green arrow representing the head pose direction.
        if frame is not None:
            nose_tip = landmarks.landmark[1]  # Nose tip landmark index.
            center_x = int(nose_tip.x * image_size[0])
            center_y = int(nose_tip.y * image_size[1])
            length = 50  # Length of the direction vector in pixels.
            # Calculate end point of the vector based on yaw and pitch.
            end_x = int(center_x + length * math.sin(math.radians(yaw)))
            end_y = int(center_y - length * math.cos(math.radians(pitch)))
            cv2.circle(frame, (center_x, center_y), 5, (0, 255, 0), -1)
            cv2.arrowedLine(frame, (center_x, center_y), (end_x, end_y), (0, 255, 0), 2)
        
        # Compute deviation as the Euclidean distance from a centered orientation (0,0).
        deviation = math.sqrt(yaw**2 + pitch**2)
        
        # Return numeric values in a dictionary.
        return {"yaw": yaw, "pitch": pitch, "deviation": deviation}

