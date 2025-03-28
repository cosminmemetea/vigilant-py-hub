from kpi.kpi_calculator import KpiCalculator
import logging
import time
import numpy as np

class FatigueCalculator(KpiCalculator):
    def __init__(self, fps=30):
        self.eye_closure_threshold = 0.2  # EAR threshold for closed eyes
        self.eye_duration_threshold = 2.0  # Seconds
        self.yawn_threshold = 0.5  # Mouth aspect ratio for yawn
        self.yawn_duration_threshold = 3.0  # Seconds
        self.eye_start_time = None
        self.yawn_start_time = None
        self.fps = fps
        logging.debug("FatigueCalculator initialized.")

    def name(self) -> str:
        return "fatigue"

    def calculate(self, landmarks, image_size, frame=None) -> str:
        if not landmarks:
            logging.warning("Fatigue: No landmarks provided.")
            self.eye_start_time = None
            self.yawn_start_time = None
            return "None"

        current_time = time.time()

        # Eye closure detection (using eyelid_openness results)
        left_ear = self._calculate_ear(landmarks, image_size, [33, 159, 145, 133])  # Left eye
        right_ear = self._calculate_ear(landmarks, image_size, [263, 386, 374, 362])  # Right eye
        avg_ear = (left_ear + right_ear) / 2
        eyes_closed = avg_ear < self.eye_closure_threshold

        # Yawn detection
        yawn_ratio = self._calculate_yawn(landmarks, image_size)

        # Eye closure timer
        if eyes_closed:
            if self.eye_start_time is None:
                self.eye_start_time = current_time
                logging.debug(f"Eyes closed started: EAR={avg_ear:.2f}")
            elif (current_time - self.eye_start_time) >= self.eye_duration_threshold:
                logging.debug(f"Fatigue (eyes closed) detected: EAR={avg_ear:.2f} for > {self.eye_duration_threshold}s")
                return "Detected (Eyes)"
        else:
            if self.eye_start_time is not None:
                logging.debug(f"Eyes opened: Duration={current_time - self.eye_start_time:.2f}s")
            self.eye_start_time = None

        # Yawn timer
        if yawn_ratio > self.yawn_threshold:
            if self.yawn_start_time is None:
                self.yawn_start_time = current_time
                logging.debug(f"Yawn started: Ratio={yawn_ratio:.2f}")
            elif (current_time - self.yawn_start_time) >= self.yawn_duration_threshold:
                logging.debug(f"Fatigue (yawn) detected: Ratio={yawn_ratio:.2f} for > {self.yawn_duration_threshold}s")
                return "Detected (Yawn)"
        else:
            if self.yawn_start_time is not None:
                logging.debug(f"Yawn ended: Duration={current_time - self.yawn_start_time:.2f}s")
            self.yawn_start_time = None

        return "None"

    def _calculate_ear(self, landmarks, image_size, indices):
        points = [landmarks.landmark[i] for i in indices]
        coords = [(p.x * image_size[0], p.y * image_size[1]) for p in points]
        vert_dist = np.linalg.norm(np.array(coords[1]) - np.array(coords[2]))
        hor_dist = np.linalg.norm(np.array(coords[0]) - np.array(coords[3]))
        return vert_dist / (hor_dist + 1e-6)

    def _calculate_yawn(self, landmarks, image_size):
        top_lip = landmarks.landmark[13]
        bottom_lip = landmarks.landmark[14]
        left_mouth = landmarks.landmark[61]
        right_mouth = landmarks.landmark[291]
        top = np.array([top_lip.x * image_size[0], top_lip.y * image_size[1]])
        bottom = np.array([bottom_lip.x * image_size[0], bottom_lip.y * image_size[1]])
        left = np.array([left_mouth.x * image_size[0], left_mouth.y * image_size[1]])
        right = np.array([right_mouth.x * image_size[0], right_mouth.y * image_size[1]])
        vertical = np.linalg.norm(bottom - top)
        horizontal = np.linalg.norm(right - left)
        return vertical / (horizontal + 1e-6) if horizontal != 0 else 0.0