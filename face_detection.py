# face_detection.py
import cv2
import mediapipe as mp
import numpy as np
from math import atan2, degrees

class FaceDetector:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils

    def process_frame(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        data = {
            "Pitch": "n.a.", "Yaw": "n.a.", "Roll": "n.a.",
            "Tilting": "n.a.", "Looking": "n.a.",
            "Blink": "No", "Yawn": "No",
            "Age": "n.a.", "Belt": "n.a."
        }

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                self.mp_drawing.draw_landmarks(
                    image=frame,
                    landmark_list=face_landmarks,
                    connections=self.mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=1),
                    connection_drawing_spec=self.mp_drawing.DrawingSpec(color=(0, 255, 255), thickness=1)
                )
                h, w, _ = frame.shape
                landmarks = [(lm.x * w, lm.y * h, lm.z * w) for lm in face_landmarks.landmark]

                nose = landmarks[1]
                left_eye = landmarks[33]
                right_eye = landmarks[263]
                data["Pitch"] = f"{self.get_pitch(nose, left_eye, right_eye):.1f}"
                data["Yaw"] = f"{self.get_yaw(nose, left_eye, right_eye):.1f}"
                data["Roll"] = f"{self.get_roll(left_eye, right_eye):.1f}"

                data["Tilting"] = self.get_tilting(data["Roll"])
                data["Looking"] = self.get_looking(data["Pitch"], data["Yaw"])
                data["Blink"] = self.detect_blink(landmarks)
                data["Yawn"] = self.detect_yawn(landmarks)

                data["Age"] = "Adult"
                data["Belt"] = "n.a."

        return frame, data

    def get_pitch(self, nose, left_eye, right_eye):
        eye_center = ((left_eye[1] + right_eye[1]) / 2)
        return degrees(atan2(nose[1] - eye_center, nose[2]))

    def get_yaw(self, nose, left_eye, right_eye):
        return degrees(atan2(right_eye[0] - left_eye[0], right_eye[2]))

    def get_roll(self, left_eye, right_eye):
        return degrees(atan2(right_eye[1] - left_eye[1], right_eye[0] - left_eye[0]))

    def get_tilting(self, roll):
        roll = float(roll)
        if roll > 8:
            return "Right"
        elif roll < -8:
            return "Left"
        return "n.a."

    def get_looking(self, pitch, yaw):
        pitch, yaw = float(pitch), float(yaw)
        if pitch > 10:
            return "Down"
        elif pitch < -10:
            return "Up"
        elif yaw > 10:
            return "Right"
        elif yaw < -10:
            return "Left"
        return "n.a."

    def detect_blink(self, landmarks):
        left_eye_top = landmarks[159][1]
        left_eye_bottom = landmarks[145][1]
        right_eye_top = landmarks[386][1]
        right_eye_bottom = landmarks[374][1]
        left_dist = left_eye_bottom - left_eye_top
        right_dist = right_eye_bottom - right_eye_top
        return "Yes" if (left_dist < 3 or right_dist < 3) else "No"

    def detect_yawn(self, landmarks):
        mouth_top = landmarks[13][1]
        mouth_bottom = landmarks[14][1]
        mouth_dist = mouth_bottom - mouth_top
        return "Yes" if mouth_dist > 25 else "No"

    def close(self):
        if self.face_mesh is not None:
            self.face_mesh.close()
            self.face_mesh = None