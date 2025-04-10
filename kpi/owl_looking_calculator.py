import logging
from kpi.kpi_calculator import KpiCalculator
from kpi.head_pose_estimator import HeadPoseEstimator

class OwlLookingCalculator(KpiCalculator):
    def __init__(self):
        self.name_str = "owl"
        self.head_pose_estimator = HeadPoseEstimator()
        # Attention zones as per Euro NCAP for Owl movements
        self.gaze_thresholds = {
            # Non-Driving Tasks (Owl)
            "driver_side_window": {"yaw": (-60, -20), "pitch": (-10, 20), "roll": (-10, 10)},
            "passenger_side_window": {"yaw": (20, 60), "pitch": (-10, 20), "roll": (-10, 10)},
            "passenger_footwell": {"yaw": (20, 60), "pitch": (-30, -10), "roll": (-10, 10)},
            "passenger_face": {"yaw": (20, 60), "pitch": (20, 40), "roll": (-10, 10)},
            "in_vehicle_infotainment": {"yaw": (0, 30), "pitch": (-30, -10), "roll": (-10, 10)},
            # Driving Tasks (Owl)
            "rear_view_mirror": {"yaw": (-20, 20), "pitch": (20, 40), "roll": (-10, 10)},
            "passenger_side_mirror": {"yaw": (20, 60), "pitch": (-10, 20), "roll": (-10, 10)},
            "driver_side_mirror": {"yaw": (-60, -20), "pitch": (-10, 20), "roll": (-10, 10)},
            # Default forward-facing position
            "forward": {"yaw": (-20, 20), "pitch": (-9.428, 9.428), "roll": (-10, 10)}  # Adjusted per your spec
        }
        logging.debug("OwlCalculator initialized.")

    def name(self) -> str:
        return self.name_str

    def classify_gaze_location(self, yaw, pitch, roll):
        """Classify the gaze location based on head pose angles for Owl-type movements."""
        for location, thresholds in self.gaze_thresholds.items():
            yaw_range = thresholds["yaw"]
            pitch_range = thresholds["pitch"]
            roll_range = thresholds["roll"]
            if (yaw_range[0] <= yaw <= yaw_range[1] and
                pitch_range[0] <= pitch <= pitch_range[1] and
                roll_range[0] <= roll <= roll_range[1]):
                logging.debug(f"Owl gaze location classified: {location}")
                return location
        logging.debug("Owl gaze location classified: unknown")
        return "unknown"

    def calculate(self, landmarks, image_size, frame=None):
        """Calculate the current Owl attention zone based on head pose."""
        pose = self.head_pose_estimator.estimate(landmarks, image_size)
        if not pose:
            logging.warning("Head pose estimation failed in OwlCalculator.")
            return "unknown"

        yaw, pitch, roll = pose["yaw"], pose["pitch"], pose["roll"]
        gaze_location = self.classify_gaze_location(yaw, pitch, roll)
        
        # Return the detected attention zone
        result = gaze_location
        logging.debug(f"OwlCalculator result: {result}")
        return result