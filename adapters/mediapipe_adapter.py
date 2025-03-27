# adapters/mediapipe_adapter.py
import mediapipe as mp

class MediaPipeAdapter:
    def __init__(self, mode="live", config: dict = None):
        """
        Initializes MediaPipe FaceMesh with the given configuration.
        :param mode: 'live' or 'static'
        :param config: Dictionary with configuration parameters.
        """
        config = config or {}
        print(f"Initializing MediaPipeAdapter with mode: {mode}")
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=(mode == "static"),
            max_num_faces=config.get("max_num_faces", 1),
            refine_landmarks=config.get("refine_landmarks", True),
            min_detection_confidence=config.get("min_detection_confidence", 0.5),
            min_tracking_confidence=config.get("min_tracking_confidence", 0.5)
        )

    def process(self, image):
        """
        Processes the image and returns facial landmarks if detected.
        :param image: RGB image (as a NumPy array)
        :return: The first detected face landmarks or None.
        """
        print("Processing image with MediaPipe...")
        results = self.face_mesh.process(image)
        if results.multi_face_landmarks:
            print(f"Detected {len(results.multi_face_landmarks)} faces")
            return results.multi_face_landmarks[0]
        print("No faces detected")
        return None