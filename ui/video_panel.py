from PyQt5 import QtWidgets, QtGui, QtCore
import cv2
import logging

class VideoPanel(QtWidgets.QWidget):
    def __init__(self, parent, tr_func, toggle_mode_cb, load_image_cb, analyze_cb):
        super().__init__(parent)
        self.tr = tr_func
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.video_label = QtWidgets.QLabel(self.tr("Video Feed"))
        self.video_label.setAlignment(QtCore.Qt.AlignCenter)
        self.video_label.setFixedSize(720, 480)
        self.set_default_style()
        layout.addWidget(self.video_label, alignment=QtCore.Qt.AlignCenter)
        
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.setSpacing(10)
        
        self.toggle_mode_btn = self.create_button("Switch to Static Mode", toggle_mode_cb, True, "#3498DB", "#2980B9")
        btn_layout.addWidget(self.toggle_mode_btn)
        
        self.load_image_btn = self.create_button("Load Static Image", load_image_cb, False, "#2ECC71", "#27AE60")
        btn_layout.addWidget(self.load_image_btn)
        
        self.analyze_btn = self.create_button("Analyze", analyze_cb, False, "#E67E22", "#D35400")
        btn_layout.addWidget(self.analyze_btn)
        
        layout.addLayout(btn_layout)
        self.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2E2E2E, stop:1 #1A1A1A); border-radius: 10px;")
        logging.debug("VideoPanel initialized.")
    
    def create_button(self, text, callback, enabled=True, color="#3498DB", hover_color="#2980B9"):
        button = QtWidgets.QPushButton(self.tr(text))
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border-radius: 6px;
                padding: 8px 16px;
                font: bold 12px "Arial";
                color: white;
                border: 1px solid #444444;
            }}
            QPushButton:disabled {{
                background-color: #7F8C8D;
            }}
            QPushButton:hover:enabled {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {hover_color};
                border: 1px solid #555555;
            }}
        """)
        button.clicked.connect(callback)
        button.setEnabled(enabled)
        return button
    
    def set_default_style(self):
        self.video_label.setStyleSheet("""
            background-color: #1C2526;
            border: 2px solid #3498DB;
            border-radius: 12px;
            font: bold 16px "Arial";
            color: #ECF0F1;
        """)
    
    def update_video_style(self, results):
        for key, value in results.items():
            if isinstance(value, str):
                if value.startswith("Detected"):
                    self.video_label.setStyleSheet("""
                        background-color: #1C2526;
                        border: 2px solid #E74C3C;
                        border-radius: 12px;
                        font: bold 16px "Arial";
                        color: #ECF0F1;
                    """)
                    return
            elif isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    if sub_value == "Detected" or sub_value in ["Long", "VATS"]:
                        self.video_label.setStyleSheet("""
                            background-color: #1C2526;
                            border: 2px solid #E74C3C;
                            border-radius: 12px;
                            font: bold 16px "Arial";
                            color: #ECF0F1;
                        """)
                        return
        self.set_default_style()