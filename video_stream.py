# video_stream.py
import cv2
from PyQt5.QtCore import QThread, pyqtSignal
import numpy as np
from face_detection import FaceDetector
import time

class VideoStream(QThread):
    frame_signal = pyqtSignal(np.ndarray)
    data_signal = pyqtSignal(dict) 

    def __init__(self):
        super().__init__()
        self.running = True
        self.cap = cv2.VideoCapture(0)
        self.face_detector = FaceDetector()

    def run(self):
        while self.running and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break
            # Process frame and get data
            processed_frame, data = self.face_detector.process_frame(frame)
            self.frame_signal.emit(processed_frame)
            self.data_signal.emit(data)
            time.sleep(0.01)  # Small delay to prevent freezing

    def stop(self):
        self.running = False
        self.cap.release()
        self.face_detector.close()
        self.quit()
        self.wait()