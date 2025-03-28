# kpi/lizard_looking_calculator.py
from kpi.kpi_calculator import KpiCalculator
from kpi.head_pose_estimator import HeadPoseEstimator
import cv2
import logging

_head_pose_estimator = HeadPoseEstimator()

class LizardLookingCalculator(KpiCalculator):
    def name(self) -> str:
        return "lizard_looking"
    
    def calculate(self, landmarks, image_size, frame=None) -> str:
        # Check if landmarks and frame are provided
        if not landmarks or frame is None:
            logging.warning("Lizard: No landmarks or frame provided.")
            return "None"
        
        # Head pose for stability check
        head_pose = _head_pose_estimator.estimate(landmarks, image_size)
        if not head_pose:
            logging.warning("Lizard: Head pose estimation failed.")
            return "None"
        yaw = head_pose.get("yaw", 0.0)
        pitch = head_pose.get("pitch", 0.0)
        head_still_threshold = 25.0  # Relaxed threshold for head stability
        
        # Eye landmarks for iris detection
        left_eye_center = landmarks.landmark[468]  # Left iris center
        right_eye_center = landmarks.landmark[473]  # Right iris center
        left_eye_outer = landmarks.landmark[33]    # Left outer corner
        right_eye_outer = landmarks.landmark[263]  # Right outer corner
        left_eye_inner = landmarks.landmark[133]   # Left inner corner
        right_eye_inner = landmarks.landmark[362]  # Right inner corner
        
        img_w, img_h = image_size
        
        # Convert to pixel coordinates
        left_eye_center_x = int(left_eye_center.x * img_w)
        right_eye_center_x = int(right_eye_center.x * img_w)
        left_eye_center_y = int(left_eye_center.y * img_h)
        right_eye_center_y = int(right_eye_center.y * img_h)
        left_eye_outer_x = int(left_eye_outer.x * img_w)
        right_eye_outer_x = int(right_eye_outer.x * img_w)
        left_eye_outer_y = int(left_eye_outer.y * img_h)
        right_eye_outer_y = int(right_eye_outer.y * img_h)
        left_eye_inner_x = int(left_eye_inner.x * img_w)
        right_eye_inner_x = int(right_eye_inner.x * img_w)
        left_eye_inner_y = int(left_eye_inner.y * img_h)
        right_eye_inner_y = int(right_eye_inner.y * img_h)
        
        # Calculate eye center as midpoint between inner and outer corners
        left_eye_mid_x = (left_eye_outer_x + left_eye_inner_x) / 2
        left_eye_mid_y = (left_eye_outer_y + left_eye_inner_y) / 2
        right_eye_mid_x = (right_eye_outer_x + right_eye_inner_x) / 2
        right_eye_mid_y = (right_eye_outer_y + right_eye_inner_y) / 2
        
        # Draw markings: blue circles for iris and direction vectors
        if frame is not None:
            # Iris points
            cv2.circle(frame, (left_eye_center_x, left_eye_center_y), 5, (255, 0, 0), -1)  # Blue circle for left iris
            cv2.circle(frame, (right_eye_center_x, right_eye_center_y), 5, (255, 0, 0), -1)  # Blue circle for right iris
            
            # Mouth points
            mouth_left = landmarks.landmark[61]  # Left mouth corner
            mouth_right = landmarks.landmark[291]  # Right mouth corner
            cv2.circle(frame, (int(mouth_left.x * img_w), int(mouth_left.y * img_h)), 3, (0, 255, 255), -1)  # Yellow
            cv2.circle(frame, (int(mouth_right.x * img_w), int(mouth_right.y * img_h)), 3, (0, 255, 255), -1)  # Yellow
            
            # Direction vectors from eye center to iris center
            left_vector_dx = left_eye_center_x - left_eye_mid_x
            left_vector_dy = left_eye_center_y - left_eye_mid_y
            right_vector_dx = right_eye_center_x - right_eye_mid_x
            right_vector_dy = right_eye_center_y - right_eye_mid_y
            length = 50  # Length of direction vector
            left_vector_end_x = int(left_eye_center_x + left_vector_dx * length / (abs(left_vector_dx) + 1e-6))
            left_vector_end_y = int(left_eye_center_y + left_vector_dy * length / (abs(left_vector_dy) + 1e-6))
            right_vector_end_x = int(right_eye_center_x + right_vector_dx * length / (abs(right_vector_dx) + 1e-6))
            right_vector_end_y = int(right_eye_center_y + right_vector_dy * length / (abs(right_vector_dy) + 1e-6))
            cv2.arrowedLine(frame, (left_eye_center_x, left_eye_center_y), 
                            (left_vector_end_x, left_vector_end_y), (255, 0, 0), 2)  # Blue vector for left
            cv2.arrowedLine(frame, (right_eye_center_x, right_eye_center_y), 
                            (right_vector_end_x, right_vector_end_y), (255, 0, 0), 2)  # Blue vector for right
        
        # Calculate iris orientation relative to frame center
        frame_center_x = img_w / 2
        frame_center_y = img_h / 2
        avg_x = (left_eye_center_x + right_eye_center_x) / 2
        avg_y = (left_eye_center_y + right_eye_center_y) / 2
        
        # Normalize positions relative to frame dimensions
        x_offset = (avg_x - frame_center_x) / (img_w * 0.5)
        y_offset = (avg_y - frame_center_y) / (img_h * 0.5)
        
        # Define thresholds for eye orientation
        center_threshold = 0.2  # Wide center zone
        directional_threshold = 0.3  # Clear directional movement
        
        # Log eye positions for debugging
        logging.debug(f"Lizard - Avg X: {x_offset:.3f}, Avg Y: {y_offset:.3f}, Yaw: {yaw:.2f}, Pitch: {pitch:.2f}")
        
        # Determine eye orientation if head is stable
        if abs(yaw) < head_still_threshold and abs(pitch) < head_still_threshold:
            if abs(x_offset) <= center_threshold and abs(y_offset) <= center_threshold:
                return "Center"
            elif x_offset > directional_threshold:
                return "Right"
            elif x_offset < -directional_threshold:
                return "Left"
            elif y_offset > directional_threshold:
                return "Down"
            elif y_offset < -directional_threshold:
                return "Up"
        return "Center"