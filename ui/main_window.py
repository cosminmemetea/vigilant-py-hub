import cv2
import numpy as np
from PyQt5 import QtWidgets, QtGui, QtCore
import logging
from ui.title_bar import TitleBar
from ui.kpi_table import KPITable
from ui.video_panel import VideoPanel
from ui.state_panel import StatePanel
from ui.translations import translations
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
        return self.translations.get(self.current_language, {}).get(text, text)
    
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
        
        main_widget = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Title bar
        self.title_bar = TitleBar(self, self.tr)
        self.title_bar.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2E2E2E, stop:1 #1A1A1A);
            border-bottom: 1px solid #444444;
        """)
        self.title_bar.language_combo.currentIndexChanged.connect(self.change_language)
        main_layout.addWidget(self.title_bar)
        
        # Main content layout
        content_widget = QtWidgets.QWidget()
        content_layout = QtWidgets.QHBoxLayout(content_widget)
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.setSpacing(20)
        
        # Left Section: State KPIs
        left_widget = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        state_kpis = self.enabled_kpis.get("state", [])
        self.state_panel = StatePanel(state_kpis, self.tr)
        left_layout.addWidget(self.state_panel)
        left_layout.addStretch()
        content_layout.addWidget(left_widget, 1)
        
        # Center Section: Video Panel
        self.video_panel = VideoPanel(self, self.tr, self.toggle_mode, self.load_static_image, 
                                      self.analyze_static_image)
        content_layout.addWidget(self.video_panel, 3)
        
        # Right Section: Numeric and Binary KPIs
        right_widget = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(15)
        
        # Top Right: Numeric KPIs
        numeric_kpis = self.enabled_kpis.get("numeric", [])
        kpi_labels = [self.tr(kpi.capitalize().replace("_", " ")) for kpi in numeric_kpis]
        self.numeric_table = KPITable(len(kpi_labels), kpi_labels, self.tr)
        self.numeric_table.setStyleSheet("""
            QTableWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2E2E2E, stop:1 #1A1A1A);
                border: 1px solid #444444;
                border-radius: 8px;
                font: 13px "Arial";
                color: #D3D3D3;
            }
            QHeaderView::section {
                background: #3498DB;
                color: white;
                padding: 5px;
                border: none;
                font: bold 14px;
            }
        """)
        right_layout.addWidget(self.numeric_table, 2)
        
        # Bottom Right: Binary KPIs
        binary_kpis = self.enabled_kpis.get("binary", [])
        binary_labels = [self.tr(kpi.capitalize().replace("_", " ")) for kpi in binary_kpis]
        self.binary_table = KPITable(len(binary_labels), binary_labels, self.tr)
        self.binary_table.setStyleSheet("""
            QTableWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2E2E2E, stop:1 #1A1A1A);
                border: 1px solid #444444;
                border-radius: 8px;
                font: 13px "Arial";
                color: #D3D3D3;
            }
            QHeaderView::section {
                background: #3498DB;
                color: white;
                padding: 5px;
                border: none;
                font: bold 14px;
            }
        """)
        right_layout.addWidget(self.binary_table, 1)
        
        content_layout.addWidget(right_widget, 1)
        
        main_layout.addWidget(content_widget)
        self.setCentralWidget(main_widget)
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #333333, stop:1 #1F1F1F);
            }
        """)
        
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
            logging.debug(f"Frame received: {frame.shape}")
            results = self.frame_processor.process_frame(frame)
            logging.debug(f"Live video results: {results}")
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QtGui.QImage(rgb_frame.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
            self.video_panel.video_label.setPixmap(QtGui.QPixmap.fromImage(qt_image))
            self.update_kpis(results)
            self.state_panel.update_states(results)
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
                self.update_kpis({})
                self.state_panel.update_states({})
    
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
        logging.debug(f"Static image analysis results: {results}")
        rgb_image = cv2.cvtColor(self.static_image, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        self.video_panel.video_label.setPixmap(QtGui.QPixmap.fromImage(qt_image))
        self.update_kpis(results)
        self.state_panel.update_states(results)
        self.video_panel.update_video_style(results)
    
    def update_kpis(self, results):
        # Numeric KPIs (Top Right Table)
        for i, key in enumerate(self.enabled_kpis.get("numeric", [])):
            value = results.get(key, "N/A")
            if isinstance(value, (int, float)):
                value = f"{value:.2f}"
            elif value is None:
                value = "N/A"
            item = self.numeric_table.item(i, 1)
            if item is None:
                item = QtWidgets.QTableWidgetItem("N/A")
                item.setForeground(QtGui.QColor("white"))
                item.setFlags(QtCore.Qt.ItemIsEnabled)
                self.numeric_table.setItem(i, 1, item)
                logging.warning(f"Reinitialized missing item at numeric table row {i}, column 1")
            item.setText(str(value))
            logging.debug(f"Updated numeric KPI {key}: {value}")
        
        # Binary KPIs (Bottom Right Table)
        for i, key in enumerate(self.enabled_kpis.get("binary", [])):
            value = results.get(key, "N/A")
            item = self.binary_table.item(i, 1)
            if item is None:
                item = QtWidgets.QTableWidgetItem("N/A")
                item.setForeground(QtGui.QColor("white"))
                item.setFlags(QtCore.Qt.ItemIsEnabled)
                self.binary_table.setItem(i, 1, item)
                logging.warning(f"Reinitialized missing item at binary table row {i}, column 1")
            item.setText(str(value))
            logging.debug(f"Updated binary KPI {key}: {value}")
    
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
        self.retranslate_ui()
        logging.info(f"Language changed to {self.current_language}")
    
    def retranslate_ui(self):
        self.setWindowTitle(self.tr("Car Face Tracker"))
        self.title_bar.title_label.setText(self.tr("Car Face Tracker"))
        self.numeric_table.setHorizontalHeaderLabels([self.tr("KPI"), self.tr("Value")])
        self.binary_table.setHorizontalHeaderLabels([self.tr("KPI"), self.tr("Value")])
        self.video_panel.video_label.setText(self.tr("Video Feed"))
        self.video_panel.toggle_mode_btn.setText(self.tr("Switch to Static Mode") if self.mode == "live" else self.tr("Switch to Live Mode"))
        self.video_panel.load_image_btn.setText(self.tr("Load Static Image"))
        self.video_panel.analyze_btn.setText(self.tr("Analyze"))
        
        for i, kpi in enumerate(self.enabled_kpis.get("numeric", [])):
            label = kpi.capitalize().replace("_", " ")
            self.numeric_table.item(i, 0).setText(self.tr(label))
        
        for i, kpi in enumerate(self.enabled_kpis.get("binary", [])):
            label = kpi.capitalize().replace("_", " ")
            self.binary_table.item(i, 0).setText(self.tr(label))
        
        self.state_panel.retranslate_ui()  # Update state panel translations
        logging.debug("UI retranslated.")
    
    def closeEvent(self, event):
        if hasattr(self, 'timer'):
            self.timer.stop()
        if hasattr(self, 'cap') and self.cap is not None and self.cap.isOpened():
            self.cap.release()
            logging.info("Camera released on application close.")
        event.accept()