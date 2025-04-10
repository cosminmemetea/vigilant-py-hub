from PyQt5 import QtWidgets, QtGui, QtCore
import logging
from ui.styles import Styles

class VideoPanel(QtWidgets.QWidget):
    def __init__(self, parent, tr_func, toggle_mode_cb, load_image_cb, analyze_cb):
        super().__init__(parent)
        self.tr = tr_func
        self.toggle_callback = toggle_mode_cb
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
        self.setStyleSheet(Styles.VIDEO_PANEL)
        logging.debug("VideoPanel initialized.")
    
    def create_button(self, text, callback, enabled=True, color="#3498DB", hover_color="#2980B9"):
        button = QtWidgets.QPushButton(self.tr(text))
        button.setStyleSheet(Styles.BUTTON(color=color, hover_color=hover_color))
        button.clicked.connect(callback)
        button.setEnabled(enabled)
        return button
    
    def set_default_style(self):
        self.video_label.setStyleSheet(Styles.VIDEO_LABEL_DEFAULT)
    
    def update_video_style(self, results):
        for value in results.values():
            if isinstance(value, str) and value.startswith("Detected"):
                self.video_label.setStyleSheet(Styles.VIDEO_LABEL_ALERT)
                return
            elif isinstance(value, dict):
                for sub_value in value.values():
                    if sub_value == "Detected":
                        self.video_label.setStyleSheet(Styles.VIDEO_LABEL_ALERT)
                        return
        self.set_default_style()
    
    def retranslate_ui(self):  # Added to update dynamically
        self.video_label.setText(self.tr("Video Feed"))
        self.toggle_mode_btn.setText(self.tr("Switch to Static Mode") if self.toggle_callback.__self__.mode == "live" else self.tr("Switch to Live Mode"))
        self.load_image_btn.setText(self.tr("Load Static Image"))
        self.analyze_btn.setText(self.tr("Analyze"))