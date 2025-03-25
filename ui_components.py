# ui_components.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHeaderView  # Add this import

class UIComponents(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()

        # Left panel: First Table
        left_panel = QVBoxLayout()
        left_label = QLabel("Metrics")
        left_label.setAlignment(Qt.AlignCenter)
        left_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFFFFF;")
        self.left_table = QTableWidget(7, 2)
        self.left_table.setHorizontalHeaderLabels(["Metric", "Value"])
        self.left_table.setStyleSheet("background-color: #2C3E50; color: #ECF0F1; border: none;")
        self.left_table.setEditTriggers(QTableWidget.NoEditTriggers)
        left_metrics = ["Pitch", "Yaw", "Roll", "Tilting", "Looking", "Blink", "Yawn"]
        for i, metric in enumerate(left_metrics):
            self.left_table.setItem(i, 0, QTableWidgetItem(metric))
            self.left_table.setItem(i, 1, QTableWidgetItem("n.a."))
        # Fix column resizing
        self.left_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Metric column
        self.left_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # Value column fills space
        left_panel.addWidget(left_label)
        left_panel.addWidget(self.left_table)

        # Center: Video Stream
        center_panel = QVBoxLayout()
        video_label = QLabel("X Face Tracker")
        video_label.setAlignment(Qt.AlignCenter)
        video_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFFFFF;")
        self.video_display = QLabel()
        self.video_display.setAlignment(Qt.AlignCenter)
        self.video_display.setMinimumSize(640, 480)
        self.video_display.setStyleSheet("background-color: #34495E; border: 2px solid #ECF0F1;")
        center_panel.addWidget(video_label)
        center_panel.addWidget(self.video_display)

        # Right panel: Right Table
        right_panel = QVBoxLayout()
        right_label = QLabel("Metrics")
        right_label.setAlignment(Qt.AlignCenter)
        right_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFFFFF;")
        self.right_table = QTableWidget(2, 2)
        self.right_table.setHorizontalHeaderLabels(["Metric", "Value"])
        self.right_table.setStyleSheet("background-color: #2C3E50; color: #ECF0F1; border: none;")
        self.right_table.setEditTriggers(QTableWidget.NoEditTriggers)
        right_metrics = ["Age", "Belt"]
        for i, metric in enumerate(right_metrics):
            self.right_table.setItem(i, 0, QTableWidgetItem(metric))
            self.right_table.setItem(i, 1, QTableWidgetItem("n.a."))
        # Fix column resizing
        self.right_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Metric column
        self.right_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # Value column fills space
        right_panel.addWidget(right_label)
        right_panel.addWidget(self.right_table)

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
        left_metrics = ["Pitch", "Yaw", "Roll", "Tilting", "Looking", "Blink", "Yawn"]
        for i, metric in enumerate(left_metrics):
            self.left_table.setItem(i, 1, QTableWidgetItem(data[metric]))
        right_metrics = ["Age", "Belt"]
        for i, metric in enumerate(right_metrics):
            self.right_table.setItem(i, 1, QTableWidgetItem(data[metric]))