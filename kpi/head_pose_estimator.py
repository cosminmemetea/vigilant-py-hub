# kpi/head_pose_estimator.py
import cv2
import numpy as np
import math

class HeadPoseEstimator:
    def __init__(self):
        # 3D model points for a generic face model (in millimeters)
        self.model_points = np.array([
            [0.0, 0.0, 0.0],             # Nose tip
            [0.0, -63.6, -12.5],         # Chin
            [-43.3, 32.7, -26.0],        # Left eye left corner
            [43.3, 32.7, -26.0],         # Right eye right corner
            [-28.9, -28.9, -24.1],       # Left mouth corner
            [28.9, -28.9, -24.1]         # Right mouth corner
        ])
        
    def estimate(self, landmarks, image_size):
        # Accesăm landmark-urile prin .landmark
        image_points = np.array([
            [landmarks.landmark[1].x * image_size[0], landmarks.landmark[1].y * image_size[1]],   # Nose tip
            [landmarks.landmark[152].x * image_size[0], landmarks.landmark[152].y * image_size[1]], # Chin
            [landmarks.landmark[33].x * image_size[0], landmarks.landmark[33].y * image_size[1]],  # Left eye
            [landmarks.landmark[263].x * image_size[0], landmarks.landmark[263].y * image_size[1]], # Right eye
            [landmarks.landmark[61].x * image_size[0], landmarks.landmark[61].y * image_size[1]],  # Left mouth
            [landmarks.landmark[291].x * image_size[0], landmarks.landmark[291].y * image_size[1]] # Right mouth
        ], dtype="double")
        
        focal_length = image_size[0]
        center = (image_size[0] / 2, image_size[1] / 2)
        camera_matrix = np.array(
            [[focal_length, 0, center[0]],
             [0, focal_length, center[1]],
             [0, 0, 1]], dtype="double"
        )
        dist_coeffs = np.zeros((4, 1))
        
        success, rotation_vector, translation_vector = cv2.solvePnP(
            self.model_points, image_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE
        )
        if not success:
            return None
        rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
        sy = np.sqrt(rotation_matrix[0, 0] ** 2 + rotation_matrix[1, 0] ** 2)
        singular = sy < 1e-6
        if not singular:
            x = math.atan2(rotation_matrix[2, 1], rotation_matrix[2, 2])
            y = math.atan2(-rotation_matrix[2, 0], sy)
            z = math.atan2(rotation_matrix[1, 0], rotation_matrix[0, 0])
        else:
            x = math.atan2(-rotation_matrix[1, 2], rotation_matrix[1, 1])
            y = math.atan2(-rotation_matrix[2, 0], sy)
            z = 0
        return {"yaw": np.degrees(y), "pitch": np.degrees(x), "roll": np.degrees(z)}