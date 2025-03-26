# ui/main_window.py
import cv2
import numpy as np
from PyQt5 import QtWidgets, QtGui, QtCore

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, frame_processor):
        super().__init__()
        self.setWindowTitle("Car Face Tracker")
        self.setMinimumSize(1200, 700)
        self.setStyleSheet("background-color: #1A252F;")
        self.mode = "live"
        self.frame_processor = frame_processor
        self.static_image = None
        
        # Main widget and layout
        main_widget = QtWidgets.QWidget()
        self.main_layout = QtWidgets.QHBoxLayout(main_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(30)
        
        # Left Panel: KPI Table for Left KPIs
        self.left_table = QtWidgets.QTableWidget(5, 2)
        self.left_table.setHorizontalHeaderLabels(["KPI", "Value"])
        self.left_table.verticalHeader().setVisible(False)
        self.left_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        kpis_left = ["Yaw", "Pitch", "Roll", "Tilt", "Yawn"]
        for i, kpi in enumerate(kpis_left):
            kpi_item = QtWidgets.QTableWidgetItem(kpi)
            kpi_item.setForeground(QtGui.QColor("white"))
            kpi_item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.left_table.setItem(i, 0, kpi_item)
            value_item = QtWidgets.QTableWidgetItem("N/A")
            value_item.setForeground(QtGui.QColor("white"))
            value_item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.left_table.setItem(i, 1, value_item)
        self.left_table.setStyleSheet("""
            QTableWidget {
                background-color: #1A252F;
                gridline-color: #3498DB;
                font: bold 14px;
                color: white;
            }
            QHeaderView::section {
                background-color: #3498DB;
                padding: 4px;
                border: none;
            }
        """)
        self.main_layout.addWidget(self.left_table, 1)
        
        # Center Panel: Video Feed and Control Buttons
        center_widget = QtWidgets.QWidget()
        center_layout = QtWidgets.QVBoxLayout(center_widget)
        center_layout.setSpacing(20)
        center_layout.setContentsMargins(0, 0, 0, 0)
        
        self.video_label = QtWidgets.QLabel("Video Feed")
        self.video_label.setAlignment(QtCore.Qt.AlignCenter)
        self.video_label.setFixedSize(800, 600)
        self.video_label.setStyleSheet("background-color: black; border: 2px solid #3498DB; border-radius: 10px;")
        center_layout.addWidget(self.video_label, alignment=QtCore.Qt.AlignCenter)
        
        btn_layout = QtWidgets.QHBoxLayout()
        self.toggle_mode_btn = QtWidgets.QPushButton("Switch to Static Mode")
        self.toggle_mode_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                border-radius: 8px;
                padding: 10px 20px;
                font: bold 12px;
                color: white;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
        """)
        self.toggle_mode_btn.clicked.connect(self.toggle_mode)
        btn_layout.addWidget(self.toggle_mode_btn)
        
        self.load_image_btn = QtWidgets.QPushButton("Load Static Image")
        self.load_image_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                border-radius: 8px;
                padding: 10px 20px;
                font: bold 12px;
                color: white;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
        """)
        self.load_image_btn.clicked.connect(self.load_static_image)
        btn_layout.addWidget(self.load_image_btn)
        
        self.analyze_btn = QtWidgets.QPushButton("Analyze")
        self.analyze_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ECC71;
                border-radius: 8px;
                padding: 10px 20px;
                font: bold 12px;
                color: white;
            }
            QPushButton:hover {
                background-color: #27AE60;
            }
        """)
        self.analyze_btn.clicked.connect(self.analyze_static_image)
        btn_layout.addWidget(self.analyze_btn)
        
        center_layout.addLayout(btn_layout)
        self.main_layout.addWidget(center_widget, 2)
        
        # Right Panel: KPI Table for Right KPIs
        self.right_table = QtWidgets.QTableWidget(2, 2)
        self.right_table.setHorizontalHeaderLabels(["KPI", "Value"])
        self.right_table.verticalHeader().setVisible(False)
        self.right_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        kpis_right = ["Adult", "Belt"]
        for i, kpi in enumerate(kpis_right):
            kpi_item = QtWidgets.QTableWidgetItem(kpi)
            kpi_item.setForeground(QtGui.QColor("white"))
            kpi_item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.right_table.setItem(i, 0, kpi_item)
            value_item = QtWidgets.QTableWidgetItem("N/A")
            value_item.setForeground(QtGui.QColor("white"))
            value_item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.right_table.setItem(i, 1, value_item)
        self.right_table.setStyleSheet("""
            QTableWidget {
                background-color: #1A252F;
                gridline-color: #3498DB;
                font: bold 14px;
                color: white;
            }
            QHeaderView::section {
                background-color: #3498DB;
                padding: 4px;
                border: none;
            }
        """)
        self.main_layout.addWidget(self.right_table, 1)
        
        self.setCentralWidget(main_widget)
        
        self.update_mode_ui()
        
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_live_video)
        if self.mode == "live":
            self.cap = cv2.VideoCapture(0)
            self.timer.start(30)
        
        self.apply_fade_in_animation()
    
    def toggle_mode(self):
        if self.mode == "live":
            self.mode = "static"
            self.toggle_mode_btn.setText("Switch to Live Mode")
            self.timer.stop()
            if hasattr(self, 'cap') and self.cap.isOpened():
                self.cap.release()
        else:
            self.mode = "live"
            self.toggle_mode_btn.setText("Switch to Static Mode")
            self.static_image = None
            self.video_label.setText("Video Feed")
            self.cap = cv2.VideoCapture(0)
            self.timer.start(30)
        self.update_mode_ui()
    
    def update_mode_ui(self):
        if self.mode == "live":
            self.load_image_btn.setEnabled(False)
            self.analyze_btn.setEnabled(False)
        else:
            self.load_image_btn.setEnabled(True)
            self.analyze_btn.setEnabled(True)
    
    def update_live_video(self):
        if not hasattr(self, 'cap') or not self.cap.isOpened():
            return
        ret, frame = self.cap.read()
        if ret:
            results = self.frame_processor.process_frame(frame)
            self.update_kpis(results)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QtGui.QImage(rgb_frame.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
            self.video_label.setPixmap(QtGui.QPixmap.fromImage(qt_image))
    
    def load_static_image(self):
        options = QtWidgets.QFileDialog.Options()
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Load Static Image", "",
                                                            "Image Files (*.png *.jpg *.jpeg)", options=options)
        if filename:
            self.static_image = cv2.imread(filename)
            rgb_image = cv2.cvtColor(self.static_image, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
            self.video_label.setPixmap(QtGui.QPixmap.fromImage(qt_image))
            self.update_kpis({})  # Reset KPIs
    
    def analyze_static_image(self):
        if self.static_image is None:
            QtWidgets.QMessageBox.warning(self, "No Image", "Please load a static image first.")
            return
        results = self.frame_processor.process_frame(self.static_image)
        print(f"Analysis results: {results}")  # Debug
        self.update_kpis(results)
    
    def update_kpis(self, results):
        # Left KPIs
        kpi_keys_left = ["yaw", "pitch", "roll", "tilt", "yawn"]
        for i, key in enumerate(kpi_keys_left):
            value = results.get(key, "N/A")
            if isinstance(value, (int, float)):
                value = f"{value:.1f}"
            elif value is None:
                value = "N/A"
            self.left_table.item(i, 1).setText(str(value))
        
        # Right KPIs
        kpi_keys_right = ["adult", "belt"]
        for i, key in enumerate(kpi_keys_right):
            value = results.get(key, "N/A")
            self.right_table.item(i, 1).setText(str(value))
    
    def apply_fade_in_animation(self):
        effect = QtWidgets.QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(effect)
        self.animation = QtCore.QPropertyAnimation(effect, b"opacity")
        self.animation.setDuration(1000)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()
    
    def closeEvent(self, event):
        if hasattr(self, 'timer'):
            self.timer.stop()
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()
        event.accept()