# static_analyzer.py
import cv2
from PyQt5.QtCore import QThread, pyqtSignal
import numpy as np
from face_detection import FaceDetector
import time

class StaticAnalyzer(QThread):
    frame_signal = pyqtSignal(np.ndarray)
    data_signal = pyqtSignal(dict)

    def __init__(self, image_path=None):
        super().__init__()
        self.running = True
        self.image_path = image_path
        self.face_detector = FaceDetector()

    def set_image(self, image_path):
        self.image_path = image_path

    def run(self):
        while self.running:
            if self.image_path:
                frame = cv2.imread(self.image_path)
                if frame is not None:
                    processed_frame, data = self.face_detector.process_frame(frame)
                    self.frame_signal.emit(processed_frame)
                    self.data_signal.emit(data)
                else:
                    self.data_signal.emit({
                        "Pitch": "n.a.", "Yaw": "n.a.", "Roll": "n.a.",
                        "Tilting": "n.a.", "Looking": "n.a.",
                        "Blink": "No", "Yawn": "No",
                        "Age": "n.a.", "Belt": "n.a."
                    })
            time.sleep(0.5)

    def stop(self):
        self.running = False
        if hasattr(self.face_detector, 'face_mesh') and self.face_detector.face_mesh is not None:
            self.face_detector.close()
        self.quit()
        self.wait()