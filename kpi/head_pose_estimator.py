import cv2
import numpy as np
import math
import logging

class HeadPoseEstimator:
    def __init__(self):
        """Initialize the HeadPoseEstimator with a 3D face model."""
        # Define 3D model points of a generic face in millimeters (reference points for PnP)
        self.model_points = np.array([
            [0.0, 0.0, 0.0],             # Nose tip (central reference point)
            [0.0, -63.6, -12.5],         # Chin (defines vertical axis)
            [-43.3, 32.7, -26.0],        # Left eye left corner (defines eye plane)
            [43.3, 32.7, -26.0],         # Right eye right corner (defines eye plane)
            [-28.9, -28.9, -24.1],       # Left mouth corner (defines mouth plane)
            [28.9, -28.9, -24.1]         # Right mouth corner (defines mouth plane)
        ], dtype="double")
        logging.debug("HeadPoseEstimator initialized with 3D model points.")

    def estimate(self, landmarks, image_size):
        """
        Estimate head pose (yaw, pitch, roll) from 2D facial landmarks.

        Args:
            landmarks: MediaPipe landmark object containing facial keypoints.
            image_size: Tuple of (width, height) of the input image.

        Returns:
            dict: Contains 'yaw', 'pitch', and 'roll' in degrees, or None if estimation fails.
        """
        # Convert 2D landmark coordinates to image pixel coordinates
        image_points = np.array([
            [landmarks.landmark[1].x * image_size[0], landmarks.landmark[1].y * image_size[1]],   # Nose tip
            [landmarks.landmark[152].x * image_size[0], landmarks.landmark[152].y * image_size[1]], # Chin
            [landmarks.landmark[33].x * image_size[0], landmarks.landmark[33].y * image_size[1]],  # Left eye left corner
            [landmarks.landmark[263].x * image_size[0], landmarks.landmark[263].y * image_size[1]], # Right eye right corner
            [landmarks.landmark[61].x * image_size[0], landmarks.landmark[61].y * image_size[1]],  # Left mouth corner
            [landmarks.landmark[291].x * image_size[0], landmarks.landmark[291].y * image_size[1]] # Right mouth corner
        ], dtype="double")

        # Camera parameters: focal length approximated as image width, center at image midpoint
        focal_length = image_size[0]  # Approximation for a typical camera
        center = (image_size[0] / 2, image_size[1] / 2)
        camera_matrix = np.array([
            [focal_length, 0, center[0]],
            [0, focal_length, center[1]],
            [0, 0, 1]
        ], dtype="double")

        # Distortion coefficients (assume no distortion for simplicity)
        dist_coeffs = np.zeros((4, 1))

        # Solve Perspective-n-Point problem to find rotation and translation vectors
        success, rotation_vector, translation_vector = cv2.solvePnP(
            self.model_points, 
            image_points, 
            camera_matrix, 
            dist_coeffs, 
            flags=cv2.SOLVEPNP_ITERATIVE  # Iterative method for accuracy
        )

        if not success:
            logging.warning("Failed to solve PnP for head pose estimation.")
            return None

        # Convert rotation vector to rotation matrix
        rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
        
        # Calculate Euler angles (yaw, pitch, roll) from rotation matrix
        sy = math.sqrt(rotation_matrix[0, 0] ** 2 + rotation_matrix[1, 0] ** 2)
        singular = sy < 1e-6  # Check for singularity (gimbal lock)

        if not singular:
            # Standard case: compute pitch (x), yaw (y), roll (z)
            pitch = math.atan2(rotation_matrix[2, 1], rotation_matrix[2, 2])  # Rotation around X-axis
            yaw = math.atan2(-rotation_matrix[2, 0], sy)                      # Rotation around Y-axis
            roll = math.atan2(rotation_matrix[1, 0], rotation_matrix[0, 0])   # Rotation around Z-axis
        else:
            # Singular case (gimbal lock): adjust computation to avoid instability
            pitch = math.atan2(-rotation_matrix[1, 2], rotation_matrix[1, 1])
            yaw = math.atan2(-rotation_matrix[2, 0], sy)
            roll = 0  # Roll becomes indeterminate in singularity

        # Convert radians to degrees and return
        result = {
            "yaw": np.degrees(yaw),
            "pitch": np.degrees(pitch),
            "roll": np.degrees(roll)
        }
        logging.debug(f"Head pose estimated: {result}")
        return result