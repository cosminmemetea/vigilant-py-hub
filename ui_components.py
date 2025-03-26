# ui_components.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QFileDialog
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHeaderView

class UIComponents(QWidget):
    def __init__(self):
        super().__init__()
        self.mode = "Live"
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()

        # Left panel: Left KPIs
        left_panel = QVBoxLayout()
        left_label = QLabel("Left KPIs")
        left_label.setAlignment(Qt.AlignCenter)
        left_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFFFFF; background-color: #2C3E50; padding: 5px;")
        self.left_table = QTableWidget(6, 2)
        self.left_table.setHorizontalHeaderLabels(["Metric", "Value"])
        self.left_table.setStyleSheet("background-color: #34495E; color: #ECF0F1; border: none; font-size: 14px;")
        self.left_table.setEditTriggers(QTableWidget.NoEditTriggers)
        left_metrics = ["Yaw", "Pitch", "Roll", "Tilt", "Looking", "Yawn"]
        for i, metric in enumerate(left_metrics):
            self.left_table.setItem(i, 0, QTableWidgetItem(metric))
            self.left_table.setItem(i, 1, QTableWidgetItem("n.a."))
        self.left_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.left_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        left_panel.addWidget(left_label)
        left_panel.addWidget(self.left_table)

        # Center: Video Stream + Controls
        center_panel = QVBoxLayout()
        video_label = QLabel("Face Tracker")
        video_label.setAlignment(Qt.AlignCenter)
        video_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFFFFF; background-color: #2C3E50; padding: 5px;")
        self.video_display = QLabel("No Image Loaded")
        self.video_display.setAlignment(Qt.AlignCenter)
        self.video_display.setMinimumSize(640, 480)
        self.video_display.setStyleSheet("background-color: #34495E; border: 2px solid #ECF0F1; color: #ECF0F1; font-size: 16px;")

        # Controls
        controls_layout = QHBoxLayout()
        self.toggle_button = QPushButton("Switch to Static")
        self.toggle_button.setStyleSheet("background-color: #3498DB; color: #FFFFFF; font-weight: bold; padding: 5px; border-radius: 5px;")
        self.load_button = QPushButton("Load Static Image")
        self.load_button.setStyleSheet("background-color: #3498DB; color: #FFFFFF; font-weight: bold; padding: 5px; border-radius: 5px;")
        self.load_button.setVisible(False)
        self.analyze_button = QPushButton("Analyze")
        self.analyze_button.setStyleSheet("background-color: #2ECC71; color: #FFFFFF; font-weight: bold; padding: 5px; border-radius: 5px;")
        self.analyze_button.setVisible(False)
        controls_layout.addWidget(self.toggle_button)
        controls_layout.addWidget(self.load_button)
        controls_layout.addWidget(self.analyze_button)

        center_panel.addWidget(video_label)
        center_panel.addWidget(self.video_display)
        center_panel.addLayout(controls_layout)

        # Right panel: Right KPIs
        right_panel = QVBoxLayout()
        right_label = QLabel("Right KPIs")
        right_label.setAlignment(Qt.AlignCenter)
        right_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFFFFF; background-color: #2C3E50; padding: 5px;")
        self.right_table = QTableWidget(2, 2)
        self.right_table.setHorizontalHeaderLabels(["Metric", "Value"])
        self.right_table.setStyleSheet("background-color: #34495E; color: #ECF0F1; border: none; font-size: 14px;")
        self.right_table.setEditTriggers(QTableWidget.NoEditTriggers)
        right_metrics = ["Adult", "Belt"]
        for i, metric in enumerate(right_metrics):
            self.right_table.setItem(i, 0, QTableWidgetItem(metric))
            self.right_table.setItem(i, 1, QTableWidgetItem("n.a."))
        self.right_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.right_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        right_panel.addWidget(right_label)
        right_panel.addWidget(self.right_table)

        main_layout.addLayout(left_panel, 1)
        main_layout.addLayout(center_panel, 3)
        main_layout.addLayout(right_panel, 1)

        self.setLayout(main_layout)
        self.setStyleSheet("background-color: #1A252F;")

    def update_frame(self, frame):
        try:
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            q_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            self.video_display.setPixmap(pixmap.scaled(self.video_display.size(), Qt.KeepAspectRatio))
        except Exception as e:
            print(f"Error updating frame: {e}")

    def update_data(self, data):
        left_metrics = ["Yaw", "Pitch", "Roll", "Tilt", "Looking", "Yawn"]
        for i, metric in enumerate(left_metrics):
            self.left_table.setItem(i, 1, QTableWidgetItem(data.get(metric, "n.a.")))
        right_metrics = ["Adult", "Belt"]
        for i, metric in enumerate(right_metrics):
            self.right_table.setItem(i, 1, QTableWidgetItem(data.get(metric, "n.a.")))

    def get_image_path(self):
        return QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")