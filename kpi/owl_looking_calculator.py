from kpi.kpi_calculator import KpiCalculator
from kpi.head_pose_estimator import HeadPoseEstimator
import cv2
import math
import logging
import numpy as np
import time
from collections import deque

# Global instance of HeadPoseEstimator for efficiency
_head_pose_estimator = HeadPoseEstimator()

class OwlLookingCalculator(KpiCalculator):
    def __init__(self, fps=30):
        """Initialize the OwlLookingCalculator with distraction thresholds and state variables.

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
        self.last_state = "Center"      # Last detected head pose direction
        self.state_start_time = time.time()  # Timestamp of last state change
        self.on_road_start_time = None  # Timestamp of last on-road period start
        self.glance_history = deque()   # History of glances: (timestamp, duration, state)
        logging.debug("OwlLookingCalculator initialized with distraction tracking.")

    def name(self) -> str:
        """Return the name of this calculator for KPI identification."""
        return "owl_looking"
    
    def calculate(self, landmarks, image_size, frame=None) -> dict:
        """Calculate head pose and distraction status.

        Args:
            landmarks: MediaPipe face landmarks object.
            image_size (tuple): Image dimensions (width, height) in pixels.
            frame: Optional OpenCV frame for drawing vectors (default None).

        Returns:
            dict: Contains 'yaw', 'pitch', 'deviation', and 'distraction' status.
        """
        # Check for valid input
        if not landmarks:
            logging.warning("Owl: No landmarks provided.")
            self._reset_state()
            return {"yaw": 0.0, "pitch": 0.0, "deviation": 0.0, "distraction": "None"}
        
        # Estimate head pose using landmarks
        head_pose = _head_pose_estimator.estimate(landmarks, image_size)
        if not head_pose:
            logging.warning("Owl: Head pose estimation failed.")
            self._reset_state()
            return {"yaw": 0.0, "pitch": 0.0, "deviation": 0.0, "distraction": "None"}
        
        # Extract yaw (horizontal) and pitch (vertical) angles in degrees
        yaw = head_pose.get("yaw", 0.0)
        pitch = head_pose.get("pitch", 0.0)
        
        # Normalize pitch to [-180, 180] range
        pitch = pitch % 360
        if pitch > 180:
            pitch -= 360
        
        # Calculate deviation as Euclidean distance from (0,0) orientation
        deviation = math.sqrt(yaw**2 + pitch**2)
        
        current_time = time.time()
        # Determine head pose direction based on yaw and pitch
        current_state = self._determine_state(yaw, pitch)

        # Update state and glance history if direction changes
        if current_state != self.last_state:
            duration = current_time - self.state_start_time
            if duration >= 0.1:  # Minimum glance duration to filter noise
                self.glance_history.append((self.state_start_time, duration, self.last_state))
                logging.debug(f"Owl glance recorded: {self.last_state} for {duration:.2f}s")
            self.state_start_time = current_time
            self.last_state = current_state
        
        # Draw head pose vector on the frame if provided
        if frame is not None:
            nose_tip = landmarks.landmark[1]  # Use nose tip as vector origin
            center_x = int(nose_tip.x * image_size[0])  # Convert X to pixel coordinate
            center_y = int(nose_tip.y * image_size[1])  # Convert Y to pixel coordinate
            length = 50  # Fixed vector length in pixels
            # Compute end point using yaw (X) and pitch (Y)
            end_x = int(center_x + length * math.sin(math.radians(yaw)))  # X: right for positive yaw
            end_y = int(center_y - length * math.cos(math.radians(pitch)))  # Y: up for positive pitch (neg Y)
            # Draw green circle at nose tip and arrow for direction
            cv2.circle(frame, (center_x, center_y), 5, (0, 255, 0), -1)
            cv2.arrowedLine(frame, (center_x, center_y), (end_x, end_y), (0, 255, 0), 2)
        
        # Check for distractions (Long or VATS)
        distraction = self._check_distractions(current_state, current_time)
        
        # Log current head pose and distraction status
        logging.debug(f"Owl - Yaw: {yaw:.2f}, Pitch: {pitch:.2f}, State: {current_state}, Distraction: {distraction}")
        return {"yaw": yaw, "pitch": pitch, "deviation": deviation, "distraction": distraction}

    def _determine_state(self, yaw, pitch):
        """Classify head pose direction based on yaw and pitch angles.

        Args:
            yaw (float): Horizontal head rotation in degrees.
            pitch (float): Vertical head rotation in degrees.

        Returns:
            str: Direction state ("Center", "Right", "Left", "Down", "Up").
        """
        threshold = 20.0  # Degrees from center considered "Center"
        if abs(yaw) <= threshold and abs(pitch) <= threshold:
            return "Center"
        elif yaw > threshold:
            return "Right"
        elif yaw < -threshold:
            return "Left"
        elif pitch > threshold:
            return "Down"
        elif pitch < -threshold:
            return "Up"
        return "Center"  # Default fallback

    def _check_distractions(self, current_state, current_time):
        """Check for Long Distraction or VATS based on head pose state and history.

        Args:
            current_state (str): Current head pose direction ("Center", "Right", etc.).
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
How to Test OwlLookingCalculator:

1. **Setup**:
   - Ensure this file is integrated into your app (e.g., registered in KpiFactory).
   - Run `python main.py` with a live camera feed enabled.
   - Verify logging is active to see debug output (e.g., via terminal).

2. **Vector Visualization**:
   - Objective: Confirm green arrows accurately reflect head pose direction.
   - Steps:
     a. Look straight ahead → Arrow should point forward or be minimal (near center).
     b. Turn head right → Arrow should point right (positive X direction).
     c. Turn head left → Arrow should point left (negative X direction).
     d. Tilt head up → Arrow should point up (negative Y direction in OpenCV coords).
     e. Tilt head down → Arrow should point down (positive Y direction).
     f. Turn head diagonally (e.g., down-right) → Arrow should point diagonally at the correct angle.
   - Expected: Arrows are 50 pixels long, starting at the nose tip (green dot), pointing in the direction of head pose.

3. **Long Distraction**:
   - Objective: Verify Long Distraction triggers after 3-4s off-road following 4s on-road.
   - Steps:
     a. Look straight (Center) for 4+ seconds → Log should show on-road time accumulating.
     b. Turn head right for 3-4 seconds → "Distraction: Long" should appear in the KPI table and log.
     c. Turn head away for < 3s or > 4s → Should remain "None".
   - Expected: "Long" appears only within 3-4s window after 4s on-road, video border turns red.

4. **VATS (Visual Attention Time Sharing)**:
   - Objective: Verify VATS triggers after 10s cumulative off-road within 30s, ending with 4s on-road.
   - Steps:
     a. Alternate turning head away and back to Center:
        - Right for 3s, Center for 2s, Left for 4s, Center for 1s, Down for 3s (total 10s off-road).
        - Then look straight (Center) for 4+ seconds.
     b. Check KPI table and log → "Distraction: VATS" should appear after the 4s on-road.
     c. If total off-road < 10s or no 4s on-road reset, should show "VATS Pending" or "None".
   - Expected: "VATS" triggers when off-road time hits 10s within 30s, confirmed by 4s on-road, border turns red.

5. **Debugging**:
   - Check logs for:
     - "Owl - Yaw: ..., Pitch: ..., State: ..., Distraction: ..."
     - "Owl glance recorded: ... for ...s"
     - "Long Distraction detected: ..." or "VATS detected: ..."
   - If vectors misalign, verify nose tip landmark (index 1) or adjust `length` (default 50).

6. **Edge Cases**:
   - No face detected → Should return {"yaw": 0.0, "pitch": 0.0, "deviation": 0.0, "distraction": "None"}.
   - Rapid head movements → Minimum 0.1s duration filters noise, ensuring stable state transitions.
"""