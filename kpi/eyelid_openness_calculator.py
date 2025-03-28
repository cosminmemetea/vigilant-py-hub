# kpi/eyelid_openness_calculator.py
from kpi.kpi_calculator import KpiCalculator
import cv2
import numpy as np
import logging

class EyelidOpennessCalculator(KpiCalculator):
    def name(self) -> str:
        return "eyelid_openness"  # Returns both left and right as a dict
    
    def calculate(self, landmarks, image_size, frame=None) -> dict:
        # Check if landmarks and frame are provided
        if not landmarks or frame is None:
            logging.warning("Eyelid: No landmarks or frame provided.")
            return {"left_eye_openness": 0.0, "right_eye_openness": 0.0}
        
        img_w, img_h = image_size
        
        # Left eye landmarks (MediaPipe indices for refined landmarks)
        left_eye_points = [
            landmarks.landmark[33],   # Left outer corner
            landmarks.landmark[159],  # Left upper eyelid
            landmarks.landmark[145],  # Left lower eyelid
            landmarks.landmark[133]   # Left inner corner
        ]
        
        # Right eye landmarks (MediaPipe indices for refined landmarks)
        right_eye_points = [
            landmarks.landmark[263],  # Right outer corner
            landmarks.landmark[386],  # Right upper eyelid
            landmarks.landmark[374],  # Right lower eyelid
            landmarks.landmark[362]   # Right inner corner
        ]
        
        # Convert to pixel coordinates
        def to_pixels(points):
            return [(int(p.x * img_w), int(p.y * img_h)) for p in points]
        
        left_eye_coords = to_pixels(left_eye_points)
        right_eye_coords = to_pixels(right_eye_points)
        
        # Calculate Eye Aspect Ratio (EAR) for openness
        def calculate_ear(eye_coords):
            # Vertical distance (upper to lower eyelid)
            vert_dist = np.linalg.norm(np.array(eye_coords[1]) - np.array(eye_coords[2]))
            # Horizontal distance (outer to inner corner)
            hor_dist = np.linalg.norm(np.array(eye_coords[0]) - np.array(eye_coords[3]))
            # EAR formula (simplified, avoid division by zero)
            ear = vert_dist / (hor_dist + 1e-6)
            return ear
        
        left_ear = calculate_ear(left_eye_coords)
        right_ear = calculate_ear(right_eye_coords)
        
        # Draw markings if frame is provided
        if frame is not None:
            # Left eye contour
            for i in range(4):
                pt1 = left_eye_coords[i]
                pt2 = left_eye_coords[(i + 1) % 4]
                cv2.line(frame, pt1, pt2, (255, 255, 0), 1)  # Cyan contour
            
            # Right eye contour
            for i in range(4):
                pt1 = right_eye_coords[i]
                pt2 = right_eye_coords[(i + 1) % 4]
                cv2.line(frame, pt1, pt2, (255, 255, 0), 1)  # Cyan contour
        
        # Log results for debugging
        logging.debug(f"Eyelid - Left EAR: {left_ear:.2f}, Right EAR: {right_ear:.2f}")
        
        return {"left_eye_openness": left_ear, "right_eye_openness": right_ear}