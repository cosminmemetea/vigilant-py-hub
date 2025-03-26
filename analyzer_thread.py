# analyzer_thread.py
import cv2
from PyQt5.QtCore import QThread, pyqtSignal
import numpy as np
from face_detection import FaceDetector
import time

class AnalyzerThread(QThread):
    frame_signal = pyqtSignal(np.ndarray)
    data_signal = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.running = True
        self.mode = "Live"
        self.cap = cv2.VideoCapture(0)
        self.face_detector = FaceDetector()
        self.static_image = None

    def set_mode(self, mode):
        self.mode = mode
        if mode == "Live" and not self.cap.isOpened():
            self.cap = cv2.VideoCapture(0)
        elif mode == "Static" and self.cap.isOpened():
            self.cap.release() 

    def set_image(self, image_path):
        frame = cv2.imread(image_path)
        if frame is not None:
            self.static_image = cv2.resize(frame, (640, 480), interpolation=cv2.INTER_AREA)
        else:
            self.static_image = None

    def run(self):
        while self.running:
            try:
                if self.mode == "Live":
                    if self.cap.isOpened():
                        ret, frame = self.cap.read()
                        if ret:
                            processed_frame, data = self.face_detector.process_frame(frame)
                            self.frame_signal.emit(processed_frame)
                            self.data_signal.emit(data)
                        else:
                            error_frame = np.zeros((480, 640, 3), dtype=np.uint8)
                            cv2.putText(error_frame, "Camera Error", (200, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                            self.frame_signal.emit(error_frame)
                            self.data_signal.emit(self.empty_data())
                        time.sleep(0.01)
                    else:
                        time.sleep(0.1)
                elif self.mode == "Static":
                    if self.static_image is not None:
                        processed_frame, data = self.face_detector.process_frame(self.static_image)
                        self.frame_signal.emit(processed_frame)
                        self.data_signal.emit(data)
                    else:
                        no_image_frame = np.zeros((480, 640, 3), dtype=np.uint8)
                        cv2.putText(no_image_frame, "No Image Loaded", (150, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                        self.frame_signal.emit(no_image_frame)
                        self.data_signal.emit(self.empty_data())
                    time.sleep(0.5)
            except Exception as e:
                print(f"Error in analyzer thread: {e}")
                time.sleep(1)  

    def empty_data(self):
        return {
            "Pitch": "n.a.", "Yaw": "n.a.", "Roll": "n.a.",
            "Tilting": "n.a.", "Looking": "n.a.",
            "Blink": "No", "Yawn": "No",
            "Age": "n.a.", "Belt": "n.a."
        }

    def stop(self):
        self.running = False
        if self.cap.isOpened():
            self.cap.release()
        self.face_detector.close()
        self.quit()
        self.wait()