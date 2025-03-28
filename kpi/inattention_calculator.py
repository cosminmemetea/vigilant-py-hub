from kpi.kpi_calculator import KpiCalculator
from kpi.head_pose_estimator import HeadPoseEstimator
import logging
import time

_head_pose_estimator = HeadPoseEstimator()

class InattentionCalculator(KpiCalculator):
    def __init__(self, fps=30):
        self.yaw_threshold = 45.0  # Degrees
        self.pitch_threshold = 30.0  # Degrees
        self.duration_threshold = 3.0  # Seconds
        self.start_time = None
        self.fps = fps  # Frames per second, adjustable
        logging.debug("InattentionCalculator initialized.")

    def name(self) -> str:
        return "inattention"

    def calculate(self, landmarks, image_size, frame=None) -> str:
        if not landmarks:
            logging.warning("Inattention: No landmarks provided.")
            self.start_time = None
            return "None"

        # Estimate head pose
        head_pose = _head_pose_estimator.estimate(landmarks, image_size)
        if not head_pose:
            logging.warning("Inattention: Head pose estimation failed.")
            self.start_time = None
            return "None"

        yaw = abs(head_pose.get("yaw", 0.0))
        pitch = abs(head_pose.get("pitch", 0.0))
        current_time = time.time()

        # Check if inattention condition is met
        is_inattentive = yaw > self.yaw_threshold or pitch > self.pitch_threshold

        if is_inattentive:
            if self.start_time is None:
                self.start_time = current_time
                logging.debug(f"Inattention started: Yaw={yaw:.2f}, Pitch={pitch:.2f}")
            elif (current_time - self.start_time) >= self.duration_threshold:
                logging.debug(f"Inattention detected: Yaw={yaw:.2f}, Pitch={pitch:.2f} for > {self.duration_threshold}s")
                return "1"
            else:
                return "0"
        else:
            if self.start_time is not None:
                logging.debug(f"Inattention ended: Duration={current_time - self.start_time:.2f}s")
            self.start_time = None
            return "None"