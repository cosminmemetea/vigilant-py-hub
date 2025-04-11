# ui/main_window.py
import cv2
import numpy as np
from PyQt5 import QtWidgets, QtGui, QtCore
import logging
from ui.title_bar import TitleBar
from ui.video_panel import VideoPanel
from ui.kpi_panel import TableKpiPanel, StateKpiPanel
from ui.translations import translations
from ui.styles import Styles

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, frame_processor, enabled_kpis):
        super().__init__()
        self.current_language = "en"
        self.frame_processor = frame_processor
        self.enabled_kpis = enabled_kpis
        self.static_image = None
        self.mode = "live"
        self.cap = None
        self.translations = translations
        self.setup_ui()
        
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_live_video)
        if self.mode == "live":
            self.initialize_camera()

    def tr(self, text):
        translated = self.translations.get(self.current_language, {}).get(text, text)
        logging.debug(f"Translating '{text}' to '{translated}' for language '{self.current_language}'")
        return translated
    
    def initialize_camera(self):
        if self.cap is not None and self.cap.isOpened():
            self.cap.release()
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            logging.error("Could not open camera.")
            QtWidgets.QMessageBox.critical(self, self.tr("Error"), self.tr("Could not access camera."))
            self.mode = "static"
            self.update_mode_ui()
        else:
            self.timer.start(30)
            logging.info("Camera initialized successfully.")
    
    def setup_ui(self):
        self.setWindowTitle(self.tr("Car Face Tracker"))
        self.setMinimumSize(1200, 700)
        self.setStyleSheet(Styles.MAIN_WINDOW)
        
        main_widget = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.title_bar = TitleBar(self, lambda x: self.tr(x))  # Pass dynamic tr function
        self.title_bar.language_combo.currentIndexChanged.connect(self.change_language)
        main_layout.addWidget(self.title_bar)
        
        content_widget = QtWidgets.QWidget()
        content_layout = QtWidgets.QHBoxLayout(content_widget)
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.setSpacing(20)
        
        self.kpi_panels = {}
        if "state" in self.enabled_kpis:
            state_panel = StateKpiPanel(self.enabled_kpis["state"], lambda x: self.tr(x), "state")
            content_layout.addWidget(state_panel, 1)
            self.kpi_panels["state"] = state_panel
        
        self.video_panel = VideoPanel(self, lambda x: self.tr(x), self.toggle_mode, self.load_static_image, self.analyze_static_image)
        content_layout.addWidget(self.video_panel, 3)
        
        right_widget = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(15)
        
        for group in self.enabled_kpis.keys() - {"state"}:
            panel = TableKpiPanel(self.enabled_kpis[group], lambda x: self.tr(x), group)
            right_layout.addWidget(panel, 2 if group == "numeric" else 1)
            self.kpi_panels[group] = panel
        
        content_layout.addWidget(right_widget, 1)
        
        main_layout.addWidget(content_widget)
        self.setCentralWidget(main_widget)
        self.update_mode_ui()
        self.apply_fade_in_animation()
    
    def toggle_mode(self):
        if self.mode == "live":
            self.mode = "static"
            self.video_panel.toggle_mode_btn.setText(self.tr("Switch to Live Mode"))
            self.timer.stop()
            if hasattr(self, 'cap') and self.cap.isOpened():
                self.cap.release()
                self.cap = None
            logging.info("Switched to static mode.")
        else:
            self.mode = "live"
            self.video_panel.toggle_mode_btn.setText(self.tr("Switch to Static Mode"))
            self.static_image = None
            self.video_panel.video_label.setText(self.tr("Video Feed"))
            self.initialize_camera()
            logging.info("Switched to live mode.")
        self.update_mode_ui()
    
    def update_mode_ui(self):
        self.video_panel.load_image_btn.setEnabled(self.mode == "static")
        self.video_panel.analyze_btn.setEnabled(self.mode == "static")
    
    def update_live_video(self):
        if not hasattr(self, 'cap') or not self.cap.isOpened():
            logging.warning("Camera is not open.")
            self.initialize_camera()
            return
        ret, frame = self.cap.read()
        if ret:
            results = self.frame_processor.process_frame(frame)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QtGui.QImage(rgb_frame.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
            self.video_panel.video_label.setPixmap(QtGui.QPixmap.fromImage(qt_image))
            for panel in self.kpi_panels.values():
                panel.update_values(results)
            self.video_panel.update_video_style(results)
        else:
            logging.error("Failed to read frame from camera.")
    
    def load_static_image(self):
        options = QtWidgets.QFileDialog.Options()
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, self.tr("Load Static Image"), "",
                                                            self.tr("Image Files (*.png *.jpg *.jpeg)"), options=options)
        if filename:
            self.static_image = cv2.imread(filename)
            if self.static_image is None:
                logging.error(f"Could not load image from {filename}")
                QtWidgets.QMessageBox.warning(self, self.tr("Error"), self.tr("Could not load image."))
            else:
                logging.info(f"Image loaded from {filename}")
                rgb_image = cv2.cvtColor(self.static_image, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                qt_image = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
                self.video_panel.video_label.setPixmap(QtGui.QPixmap.fromImage(qt_image))
                for panel in self.kpi_panels.values():
                    panel.update_values({})
    
    def analyze_static_image(self):
        if self.static_image is None:
            QtWidgets.QMessageBox.warning(self, self.tr("No Image"), self.tr("Please load a static image first."))
            return
        logging.info("Analyzing static image...")
        from adapters.mediapipe_adapter import MediaPipeAdapter
        self.frame_processor.mediapipe_adapter = MediaPipeAdapter(mode="static", config={
            "max_num_faces": 1,
            "refine_landmarks": True,
            "min_detection_confidence": 0.5,
            "min_tracking_confidence": 0.5
        })
        results = self.frame_processor.process_frame(self.static_image)
        rgb_image = cv2.cvtColor(self.static_image, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        self.video_panel.video_label.setPixmap(QtGui.QPixmap.fromImage(qt_image))
        for panel in self.kpi_panels.values():
            panel.update_values(results)
        self.video_panel.update_video_style(results)
    
    def apply_fade_in_animation(self):
        effect = QtWidgets.QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(effect)
        self.animation = QtCore.QPropertyAnimation(effect, b"opacity")
        self.animation.setDuration(1000)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()
    
    def change_language(self, index):
        languages = ["en", "fr", "de", "ro"]
        self.current_language = languages[index]
        logging.debug(f"Language changing to {self.current_language}")
        self.retranslate_ui()
        logging.info(f"Language changed to {self.current_language}")
    
    def retranslate_ui(self):
        self.setWindowTitle(self.tr("Car Face Tracker"))
        self.title_bar.title_label.setText(self.tr("Car Face Tracker"))
        self.video_panel.retranslate_ui()  # Explicitly call subcomponent retranslate
        for panel in self.kpi_panels.values():
            panel.retranslate_ui()
        logging.debug("MainWindow UI retranslated")
    
    def closeEvent(self, event):
        if hasattr(self, 'timer'):
            self.timer.stop()
        if hasattr(self, 'cap') and self.cap is not None and self.cap.isOpened():
            self.cap.release()
            logging.info("Camera released on application close.")
        event.accept()
