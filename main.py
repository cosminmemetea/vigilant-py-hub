# main.py
import sys
import cv2
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from ui_components import UIComponents
from face_detection import FaceDetector
import numpy as np

class MainApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.ui = UIComponents()
        self.face_detector = FaceDetector()
        self.mode = "Live"
        self.cap = cv2.VideoCapture(0)
        self.static_image = None
        self.static_frame = None
        self.static_data = None

        # Timer pentru Live
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_live)
        self.timer.start(10)  # 10ms ~ 100 FPS

        # Conectăm butoanele
        self.ui.toggle_button.clicked.connect(self.toggle_mode)
        self.ui.load_button.clicked.connect(self.load_image)
        self.ui.analyze_button.clicked.connect(self.analyze_image)

        self.ui.showMaximized()

    def update_live(self):
        if self.mode == "Live" and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                processed_frame, data = self.face_detector.process_frame(frame)
                self.ui.update_frame(processed_frame)
                self.ui.update_data(data)
            else:
                error_frame = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(error_frame, "Camera Error", (200, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                self.ui.update_frame(error_frame)
                self.ui.update_data(self.face_detector.empty_data())

    def toggle_mode(self):
        if self.mode == "Live":
            self.mode = "Static"
            if self.cap.isOpened():
                self.cap.release()
            self.ui.toggle_button.setText("Switch to Live")
            self.ui.load_button.setVisible(True)
            self.ui.analyze_button.setVisible(False)
            self.static_image = None
            self.static_frame = None
            self.static_data = None
            no_image_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(no_image_frame, "No Image Loaded", (150, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            self.ui.update_frame(no_image_frame)
            self.ui.update_data(self.face_detector.empty_data())
        else:
            self.mode = "Live"
            self.cap = cv2.VideoCapture(0)
            self.ui.toggle_button.setText("Switch to Static")
            self.ui.load_button.setVisible(False)
            self.ui.analyze_button.setVisible(False)

    def load_image(self):
        if self.mode == "Static":
            image_path, _ = self.ui.get_image_path()
            if image_path:
                frame = cv2.imread(image_path)
                if frame is not None:
                    self.static_image = cv2.resize(frame, (640, 480), interpolation=cv2.INTER_AREA)
                    self.static_frame = self.static_image.copy()
                    self.static_data = self.face_detector.empty_data()
                    self.ui.update_frame(self.static_frame)
                    self.ui.update_data(self.static_data)
                    self.ui.analyze_button.setVisible(True)

    def analyze_image(self):
        if self.mode == "Static" and self.static_image is not None:
            self.static_frame, self.static_data = self.face_detector.process_frame(self.static_image)
            self.ui.update_frame(self.static_frame)
            self.ui.update_data(self.static_data)
            self.ui.analyze_button.setVisible(False)

    def closeEvent(self, event):
        self.timer.stop()
        if self.cap.isOpened():
            self.cap.release()
        self.face_detector.close()
        event.accept()

if __name__ == "__main__":
    app = MainApp(sys.argv)
    sys.exit(app.exec_())