from PyQt5 import QtWidgets, QtGui, QtCore
import cv2
import logging

class VideoPanel(QtWidgets.QWidget):
    def __init__(self, parent, tr_func, toggle_mode_cb, load_image_cb, analyze_cb):
        super().__init__(parent)
        self.tr = tr_func
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.video_label = QtWidgets.QLabel(self.tr("Video Feed"))
        self.video_label.setAlignment(QtCore.Qt.AlignCenter)
        self.video_label.setFixedSize(800, 600)
        self.set_default_style()
        layout.addWidget(self.video_label, alignment=QtCore.Qt.AlignCenter)
        
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.setSpacing(15)
        
        self.toggle_mode_btn = self.create_button("Switch to Static Mode", toggle_mode_cb, True)
        btn_layout.addWidget(self.toggle_mode_btn)
        
        self.load_image_btn = self.create_button("Load Static Image", load_image_cb, False)
        btn_layout.addWidget(self.load_image_btn)
        
        self.analyze_btn = self.create_button("Analyze", analyze_cb, False, "#2ECC71", "#27AE60")
        btn_layout.addWidget(self.analyze_btn)
        
        layout.addLayout(btn_layout)
        logging.debug("VideoPanel initialized.")
    
    def create_button(self, text, callback, enabled=True, color="#3498DB", hover_color="#2980B9"):
        button = QtWidgets.QPushButton(self.tr(text))
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border-radius: 8px;
                padding: 10px 20px;
                font: bold 12px;
                color: white;
            }}
            QPushButton:disabled {{
                background-color: #7F8C8D;
            }}
            QPushButton:hover:enabled {{
                background-color: {hover_color};
            }}
        """)
        button.clicked.connect(callback)
        button.setEnabled(enabled)
        return button
    
    def set_default_style(self):
        self.video_label.setStyleSheet("""
            background-color: black;
            border: 2px solid #3498DB;
            border-radius: 10px;
            font: bold 16px;
            color: white;
        """)
    
    def update_video_style(self, results):
        inattention = results.get("inattention", "None")
        fatigue = results.get("fatigue", "None")
        owl_result = results.get("owl_looking", "None")
        lizard_result = results.get("lizard_looking", "None")
        sleep_result = results.get("sleep", {"microsleep": "None", "sleep": "None"})
        
        owl_distraction = owl_result.get("distraction", "None") if isinstance(owl_result, dict) else owl_result
        lizard_distraction = lizard_result.get("distraction", "None") if isinstance(lizard_result, dict) else lizard_result
        # Handle both dict and string cases for sleep_result
        microsleep_status = sleep_result.get("microsleep", "None") if isinstance(sleep_result, dict) else "None"
        sleep_status = sleep_result.get("sleep", "None") if isinstance(sleep_result, dict) else "None"
        
        if (inattention == "Detected" or 
            fatigue.startswith("Detected") or 
            owl_distraction in ["Long", "VATS"] or 
            lizard_distraction in ["Long", "VATS"] or 
            microsleep_status == "Detected" or 
            sleep_status == "Detected"):
            self.video_label.setStyleSheet("""
                background-color: black;
                border: 2px solid red;
                border-radius: 10px;
                font: bold 16px;
                color: white;
            """)
        else:
            self.set_default_style()