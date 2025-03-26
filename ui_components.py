# ui_components.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QFileDialog
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHeaderView

class UIComponents(QWidget):
    def __init__(self, analyzer):
        super().__init__()
        self.analyzer = analyzer  # Referință directă la analyzer
        self.mode = "Live"
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()

        # Left panel: DMS Table
        left_panel = QVBoxLayout()
        dms_label = QLabel("DMS Metrics")
        dms_label.setAlignment(Qt.AlignCenter)
        dms_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFFFFF;")
        self.dms_table = QTableWidget(7, 2)
        self.dms_table.setHorizontalHeaderLabels(["Metric", "Value"])
        self.dms_table.setStyleSheet("background-color: #2C3E50; color: #ECF0F1; border: none;")
        self.dms_table.setEditTriggers(QTableWidget.NoEditTriggers)
        dms_metrics = ["Pitch", "Yaw", "Roll", "Tilting", "Looking", "Blink", "Yawn"]
        for i, metric in enumerate(dms_metrics):
            self.dms_table.setItem(i, 0, QTableWidgetItem(metric))
            self.dms_table.setItem(i, 1, QTableWidgetItem("n.a."))
        self.dms_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.dms_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        left_panel.addWidget(dms_label)
        left_panel.addWidget(self.dms_table)

        # Center: Video Stream + Controls
        center_panel = QVBoxLayout()
        video_label = QLabel("Face Tracker")
        video_label.setAlignment(Qt.AlignCenter)
        video_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFFFFF;")
        self.video_display = QLabel("No Image Loaded")
        self.video_display.setAlignment(Qt.AlignCenter)
        self.video_display.setMinimumSize(640, 480)
        self.video_display.setStyleSheet("background-color: #34495E; border: 2px solid #ECF0F1; color: #ECF0F1; font-size: 16px;")

        # Controls
        controls_layout = QHBoxLayout()
        self.toggle_button = QPushButton("Switch to Static")
        self.toggle_button.setStyleSheet("background-color: #3498DB; color: #FFFFFF; font-weight: bold;")
        self.load_button = QPushButton("Load Static Image")
        self.load_button.setStyleSheet("background-color: #3498DB; color: #FFFFFF; font-weight: bold;")
        self.load_button.clicked.connect(self.load_image)
        self.load_button.setVisible(False) 
        controls_layout.addWidget(self.toggle_button)
        controls_layout.addWidget(self.load_button)

        center_panel.addWidget(video_label)
        center_panel.addWidget(self.video_display)
        center_panel.addLayout(controls_layout)

        # Right panel: OMS Table
        right_panel = QVBoxLayout()
        oms_label = QLabel("OMS Metrics")
        oms_label.setAlignment(Qt.AlignCenter)
        oms_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFFFFF;")
        self.oms_table = QTableWidget(2, 2)
        self.oms_table.setHorizontalHeaderLabels(["Metric", "Value"])
        self.oms_table.setStyleSheet("background-color: #2C3E50; color: #ECF0F1; border: none;")
        self.oms_table.setEditTriggers(QTableWidget.NoEditTriggers)
        oms_metrics = ["Age", "Belt"]
        for i, metric in enumerate(oms_metrics):
            self.oms_table.setItem(i, 0, QTableWidgetItem(metric))
            self.oms_table.setItem(i, 1, QTableWidgetItem("n.a."))
        self.oms_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.oms_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        right_panel.addWidget(oms_label)
        right_panel.addWidget(self.oms_table)

        main_layout.addLayout(left_panel, 1)
        main_layout.addLayout(center_panel, 3)
        main_layout.addLayout(right_panel, 1)

        self.setLayout(main_layout)
        self.setStyleSheet("background-color: #1A252F;")

    def update_frame(self, frame):
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        q_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        self.video_display.setPixmap(pixmap.scaled(self.video_display.size(), Qt.KeepAspectRatio))

    def update_data(self, data):
        dms_metrics = ["Pitch", "Yaw", "Roll", "Tilting", "Looking", "Blink", "Yawn"]
        for i, metric in enumerate(dms_metrics):
            self.dms_table.setItem(i, 1, QTableWidgetItem(data[metric]))
        oms_metrics = ["Age", "Belt"]
        for i, metric in enumerate(oms_metrics):
            self.oms_table.setItem(i, 1, QTableWidgetItem(data[metric]))

    def load_image(self):
        image_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if image_path:
            self.analyzer.set_image(image_path)
            self.video_display.setText("")  