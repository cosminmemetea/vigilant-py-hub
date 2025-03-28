from kpi.kpi_calculator import KpiCalculator
from kpi.head_pose_estimator import HeadPoseEstimator
import cv2
import logging
import time
from collections import deque
import numpy as np
import math

# Global instance of HeadPoseEstimator for efficiency
_head_pose_estimator = HeadPoseEstimator()

class LizardLookingCalculator(KpiCalculator):
    def __init__(self, fps=30):
        """Initialize the LizardLookingCalculator with distraction thresholds and state variables.

        Args:
            fps (int): Frames per second, default 30, used for timing calculations.
        """
        self.fps = fps  # Frames per second for timing consistency
        # Long Distraction: 3-4 seconds off-road after 4 seconds on-road
        self.long_distraction_min = 3.0  # Minimum duration for Long Distraction (seconds)
        self.long_distraction_max = 4.0  # Maximum duration for Long Distraction (seconds)
        self.on_road_preceding = 4.0    # Required preceding on-road gaze (seconds)
        # VATS (Visual Attention Time Sharing): 10 seconds off-road within 30 seconds
        self.vats_threshold = 10.0      # Cumulative off-road time for VATS (seconds)
        self.vats_window = 30.0         # Time window for VATS detection (seconds)
        self.on_road_reset = 4.0        # On-road duration to reset VATS (seconds)
        
        # State tracking variables
        self.last_state = "Center"      # Last detected gaze direction
        self.state_start_time = time.time()  # Timestamp of last state change
        self.on_road_start_time = None  # Timestamp of last on-road period start
        self.glance_history = deque()   # History of glances: (timestamp, duration, state)
        logging.debug("LizardLookingCalculator initialized with distraction tracking.")

    def name(self) -> str:
        """Return the name of this calculator for KPI identification."""
        return "lizard_looking"
    
    def calculate(self, landmarks, image_size, frame=None) -> dict:
        """Calculate eye gaze direction and distraction status.

        Args:
            landmarks: MediaPipe face landmarks object.
            image_size (tuple): Image dimensions (width, height) in pixels.
            frame: Optional OpenCV frame for drawing vectors (default None).

        Returns:
            dict: Contains 'direction' (gaze state) and 'distraction' (distraction status).
        """
        # Check for valid input
        if not landmarks or frame is None:
            logging.warning("Lizard: No landmarks or frame provided.")
            self._reset_state()
            return {"direction": "None", "distraction": "None"}
        
        # Estimate head pose to ensure head is relatively still
        head_pose = _head_pose_estimator.estimate(landmarks, image_size)
        if not head_pose:
            logging.warning("Lizard: Head pose estimation failed.")
            self._reset_state()
            return {"direction": "None", "distraction": "None"}
        
        yaw = head_pose.get("yaw", 0.0)    # Head horizontal rotation (degrees)
        pitch = head_pose.get("pitch", 0.0)  # Head vertical rotation (degrees)
        head_still_threshold = 25.0         # Threshold for head stability (degrees)
        
        # Extract eye landmarks
        left_eye_center = landmarks.landmark[468]  # Left iris center
        right_eye_center = landmarks.landmark[473]  # Right iris center
        left_eye_outer = landmarks.landmark[33]    # Left outer corner
        right_eye_outer = landmarks.landmark[263]  # Right outer corner
        left_eye_inner = landmarks.landmark[133]   # Left inner corner
        right_eye_inner = landmarks.landmark[362]  # Right inner corner
        
        img_w, img_h = image_size  # Image width and height
        
        # Convert landmark coordinates to pixel values
        left_eye_center_x = int(left_eye_center.x * img_w)
        left_eye_center_y = int(left_eye_center.y * img_h)
        right_eye_center_x = int(right_eye_center.x * img_w)
        right_eye_center_y = int(right_eye_center.y * img_h)
        left_eye_outer_x = int(left_eye_outer.x * img_w)
        left_eye_outer_y = int(left_eye_outer.y * img_h)
        right_eye_outer_x = int(right_eye_outer.x * img_w)
        right_eye_outer_y = int(right_eye_outer.y * img_h)
        left_eye_inner_x = int(left_eye_inner.x * img_w)
        left_eye_inner_y = int(left_eye_inner.y * img_h)
        right_eye_inner_x = int(right_eye_inner.x * img_w)
        right_eye_inner_y = int(right_eye_inner.y * img_h)
        
        # Calculate eye midpoints as reference for gaze direction
        left_eye_mid_x = (left_eye_outer_x + left_eye_inner_x) / 2
        left_eye_mid_y = (left_eye_outer_y + left_eye_inner_y) / 2
        right_eye_mid_x = (right_eye_outer_x + right_eye_inner_x) / 2
        right_eye_mid_y = (right_eye_outer_y + right_eye_inner_y) / 2
        
        # Compute vector displacements from midpoint to iris center
        left_dx = left_eye_center_x - left_eye_mid_x  # Horizontal displacement (left eye)
        left_dy = left_eye_center_y - left_eye_mid_y  # Vertical displacement (left eye)
        right_dx = right_eye_center_x - right_eye_mid_x  # Horizontal (right eye)
        right_dy = right_eye_center_y - right_eye_mid_y  # Vertical (right eye)
        
        # Normalize vectors to a fixed length of 50 pixels
        length = 50  # Fixed vector length in pixels
        left_magnitude = math.sqrt(left_dx**2 + left_dy**2)  # Magnitude of left eye vector
        right_magnitude = math.sqrt(right_dx**2 + right_dy**2)  # Magnitude of right eye vector
        
        # Prevent division by zero with a small epsilon
        left_magnitude = max(left_magnitude, 1e-6)
        right_magnitude = max(right_magnitude, 1e-6)
        
        # Scale vectors to fixed length while preserving direction
        left_vector_x = left_dx * length / left_magnitude
        left_vector_y = left_dy * length / left_magnitude
        right_vector_x = right_dx * length / right_magnitude
        right_vector_y = right_dy * length / right_magnitude
        
        # Calculate end points for drawing
        left_end_x = int(left_eye_center_x + left_vector_x)
        left_end_y = int(left_eye_center_y + left_vector_y)
        right_end_x = int(right_eye_center_x + right_vector_x)
        right_end_y = int(right_eye_center_y + right_vector_y)
        
        # Draw gaze vectors on the frame if provided
        if frame is not None:
            # Draw iris centers as blue circles
            cv2.circle(frame, (left_eye_center_x, left_eye_center_y), 5, (255, 0, 0), -1)
            cv2.circle(frame, (right_eye_center_x, right_eye_center_y), 5, (255, 0, 0), -1)
            # Draw direction vectors as blue arrows
            cv2.arrowedLine(frame, (left_eye_center_x, left_eye_center_y), 
                            (left_end_x, left_end_y), (255, 0, 0), 2)
            cv2.arrowedLine(frame, (right_eye_center_x, right_eye_center_y), 
                            (right_end_x, right_end_y), (255, 0, 0), 2)
        
        # Determine gaze direction for distraction logic (relative to frame center)
        frame_center_x = img_w / 2
        frame_center_y = img_h / 2
        avg_x = (left_eye_center_x + right_eye_center_x) / 2  # Average X of both irises
        avg_y = (left_eye_center_y + right_eye_center_y) / 2  # Average Y of both irises
        x_offset = (avg_x - frame_center_x) / (img_w * 0.5)   # Normalized X offset
        y_offset = (avg_y - frame_center_y) / (img_h * 0.5)   # Normalized Y offset
        
        # Thresholds for gaze direction classification
        center_threshold = 0.2       # Zone considered "Center"
        directional_threshold = 0.3  # Threshold for directional gaze
        current_time = time.time()

        # Classify gaze direction based on offsets and head stability
        current_state = "Center"
        if abs(yaw) < head_still_threshold and abs(pitch) < head_still_threshold:
            if abs(x_offset) <= center_threshold and abs(y_offset) <= center_threshold:
                current_state = "Center"
            elif x_offset > directional_threshold:
                current_state = "Right"
            elif x_offset < -directional_threshold:
                current_state = "Left"
            elif y_offset > directional_threshold:
                current_state = "Down"
            elif y_offset < -directional_threshold:
                current_state = "Up"

        # Update state and glance history for distraction detection
        if current_state != self.last_state:
            duration = current_time - self.state_start_time
            if duration >= 0.1:  # Minimum glance duration to filter noise
                self.glance_history.append((self.state_start_time, duration, self.last_state))
                logging.debug(f"Lizard glance recorded: {self.last_state} for {duration:.2f}s")
            self.state_start_time = current_time
            self.last_state = current_state
        
        # Check for distractions (Long or VATS)
        distraction = self._check_distractions(current_state, current_time)
        
        # Log current gaze and distraction status
        logging.debug(f"Lizard - X Offset: {x_offset:.3f}, Y Offset: {y_offset:.3f}, State: {current_state}, Distraction: {distraction}")
        return {"direction": current_state, "distraction": distraction}

    def _check_distractions(self, current_state, current_time):
        """Check for Long Distraction or VATS based on gaze state and history.

        Args:
            current_state (str): Current gaze direction ("Center", "Right", etc.).
            current_time (float): Current timestamp in seconds.

        Returns:
            str: Distraction status ("None", "Long", "VATS", "VATS Pending").
        """
        # Remove glances outside the 30-second VATS window
        while self.glance_history and (current_time - self.glance_history[0][0]) > self.vats_window:
            self.glance_history.popleft()

        # Check for Long Distraction
        if current_state != "Center":
            duration = current_time - self.state_start_time
            if self.long_distraction_min <= duration <= self.long_distraction_max:
                if self.on_road_start_time and self.state_start_time - self.on_road_start_time >= self.on_road_preceding:
                    logging.debug(f"Long Distraction detected: {duration:.2f}s off-road after {self.on_road_start_time - self.state_start_time:.2f}s on-road")
                    return "Long"
        else:
            # Update on-road start time when centered
            if self.last_state == "Center":
                self.on_road_start_time = self.state_start_time

        # Check for VATS (Visual Attention Time Sharing)
        if current_state == "Center":
            duration = current_time - self.state_start_time
            if duration >= self.on_road_reset:  # 4s on-road resets or triggers VATS
                off_road_time = sum(d for t, d, s in self.glance_history if s != "Center")
                if off_road_time >= self.vats_threshold:
                    logging.debug(f"VATS detected: {off_road_time:.2f}s off-road in last {self.vats_window}s")
                    self.glance_history.clear()
                    return "VATS"
                self.glance_history.clear()
        else:
            off_road_time = sum(d for t, d, s in self.glance_history if s != "Center")
            current_off_road = current_time - self.state_start_time
            if off_road_time + current_off_road >= self.vats_threshold:
                logging.debug(f"VATS pending: {off_road_time + current_off_road:.2f}s off-road in last {self.vats_window}s")
                return "VATS Pending"

        return "None"

    def _reset_state(self):
        """Reset state variables to initial values."""
        self.last_state = "Center"
        self.state_start_time = time.time()
        self.on_road_start_time = None
        self.glance_history.clear()

# -----------------------------------
# Testing Instructions
# -----------------------------------
"""
How to Test LizardLookingCalculator:

1. **Setup**:
   - Ensure this file is integrated into your app (e.g., registered in KpiFactory).
   - Run `python main.py` with a live camera feed enabled.
   - Verify logging is active to see debug output (e.g., via terminal).

2. **Vector Visualization**:
   - Objective: Confirm blue arrows accurately reflect eye gaze direction.
   - Steps:
     a. Look straight ahead → Arrows should point minimally or not at all (near center).
     b. Look right → Arrows should point right (positive X direction).
     c. Look left → Arrows should point left (negative X direction).
     d. Look up → Arrows should point up (negative Y direction in OpenCV coords).
     e. Look down → Arrows should point down (positive Y direction).
     f. Look diagonally (e.g., up-left) → Arrows should point diagonally at the correct angle.
   - Expected: Arrows are 50 pixels long, starting at iris centers, pointing in the direction of gaze.

3. **Long Distraction**:
   - Objective: Verify Long Distraction triggers after 3-4s off-road following 4s on-road.
   - Steps:
     a. Look straight (Center) for 4+ seconds → Log should show on-road time accumulating.
     b. Look away (e.g., right) for 3-4 seconds → "Distraction: Long" should appear in the KPI table and log.
     c. Look away for < 3s or > 4s → Should remain "None".
   - Expected: "Long" appears only within 3-4s window after 4s on-road, video border turns red.

4. **VATS (Visual Attention Time Sharing)**:
   - Objective: Verify VATS triggers after 10s cumulative off-road within 30s, ending with 4s on-road.
   - Steps:
     a. Alternate looking away (e.g., left, right) and back to Center:
        - Look left for 3s, Center for 2s, right for 4s, Center for 1s, down for 3s (total 10s off-road).
        - Then look straight (Center) for 4+ seconds.
     b. Check KPI table and log → "Distraction: VATS" should appear after the 4s on-road.
     c. If total off-road < 10s or no 4s on-road reset, should show "VATS Pending" or "None".
   - Expected: "VATS" triggers when off-road time hits 10s within 30s, confirmed by 4s on-road, border turns red.

5. **Debugging**:
   - Check logs for:
     - "Lizard - X Offset: ..., Y Offset: ..., State: ..., Distraction: ..."
     - "Lizard glance recorded: ... for ...s"
     - "Long Distraction detected: ..." or "VATS detected: ..."
   - If vectors misalign, verify landmark indices (468, 473 for irises) or adjust `length` (default 50).

6. **Edge Cases**:
   - No face detected → Should return {"direction": "None", "distraction": "None"}.
   - Head tilted beyond 25° (yaw/pitch) → Gaze defaults to "Center" to avoid false positives.
"""