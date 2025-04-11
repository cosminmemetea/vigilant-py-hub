# ui/video_panel.py
# Defines the VideoPanel class, a PyQt5 widget for displaying video feed and control buttons.

from PyQt5 import QtWidgets, QtGui, QtCore  # PyQt5 modules for creating GUI components.
import logging  # Facilitates logging for debugging and monitoring UI initialization.
from ui.styles import Styles  # Custom styles for consistent UI appearance.

class VideoPanel(QtWidgets.QWidget):
    def __init__(self, parent, tr_func, toggle_mode_cb, load_image_cb, analyze_cb):
        """Initialize the VideoPanel with video display and control buttons.

        Args:
            parent: Parent widget for this panel.
            tr_func: Translation function for internationalization.
            toggle_mode_cb: Callback to toggle between live and static modes.
            load_image_cb: Callback to load a static image.
            analyze_cb: Callback to analyze the current frame or image.
        """
        super().__init__(parent)  # Initialize base QWidget class.
        self.tr = tr_func  # Store translation function for dynamic text updates.
        self.toggle_callback = toggle_mode_cb  # Store mode toggle callback.
        layout = QtWidgets.QVBoxLayout(self)  # Create vertical layout for the panel.
        layout.setSpacing(15)  # Set spacing between widgets.
        layout.setContentsMargins(0, 0, 0, 0)  # Remove default margins.
        
        # Create label to display video feed or static image.
        self.video_label = QtWidgets.QLabel(self.tr("Video Feed"))
        self.video_label.setAlignment(QtCore.Qt.AlignCenter)  # Center the content.
        self.video_label.setFixedSize(720, 480)  # Set fixed dimensions for video display.
        self.set_default_style()  # Apply default styling to video label.
        layout.addWidget(self.video_label, alignment=QtCore.Qt.AlignCenter)  # Add label to layout.
        
        # Create horizontal layout for control buttons.
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.setSpacing(10)  # Set spacing between buttons.
        
        # Create button to toggle between live and static modes.
        self.toggle_mode_btn = self.create_button("Switch to Static Mode", toggle_mode_cb, True, "#3498DB", "#2980B9")
        btn_layout.addWidget(self.toggle_mode_btn)
        
        # Create button to load a static image.
        self.load_image_btn = self.create_button("Load Static Image", load_image_cb, False, "#2ECC71", "#27AE60")
        btn_layout.addWidget(self.load_image_btn)
        
        # Create button to trigger analysis.
        self.analyze_btn = self.create_button("Analyze", analyze_cb, False, "#E67E22", "#D35400")
        btn_layout.addWidget(self.analyze_btn)
        
        layout.addLayout(btn_layout)  # Add button layout to main layout.
        self.setStyleSheet(Styles.VIDEO_PANEL)  # Apply panel-wide styling.
        logging.debug("VideoPanel initialized.")
    
    def create_button(self, text, callback, enabled=True, color="#3498DB", hover_color="#2980B9"):
        """Create a styled button with the given text and callback.

        Args:
            text: Button label text (translated).
            callback: Function to call when the button is clicked.
            enabled: Whether the button is initially enabled (default: True).
            color: Background color for the button.
            hover_color: Background color when the button is hovered.

        Returns:
            QtWidgets.QPushButton: Configured button instance.
        """
        button = QtWidgets.QPushButton(self.tr(text))  # Create button with translated text.
        button.setStyleSheet(Styles.BUTTON(color=color, hover_color=hover_color))  # Apply custom styling.
        button.clicked.connect(callback)  # Connect button click to callback.
        button.setEnabled(enabled)  # Set initial enabled state.
        return button
    
    def set_default_style(self):
        """Apply default styling to the video label."""
        self.video_label.setStyleSheet(Styles.VIDEO_LABEL_DEFAULT)
    
    def update_video_style(self, results):
        """Update video label styling based on KPI results.

        Args:
            results: Dictionary of KPI results to check for alerts.
        """
        for value in results.values():
            # Check for string-based alerts (e.g., "Detected").
            if isinstance(value, str) and value.startswith("Detected"):
                self.video_label.setStyleSheet(Styles.VIDEO_LABEL_ALERT)  # Apply alert styling.
                return
            # Check for nested dictionary alerts.
            elif isinstance(value, dict):
                for sub_value in value.values():
                    if sub_value == "Detected":
                        self.video_label.setStyleSheet(Styles.VIDEO_LABEL_ALERT)  # Apply alert styling.
                        return
        self.set_default_style()  # Revert to default styling if no alerts.
    
    def retranslate_ui(self):
        """Update UI text with translated strings for dynamic language changes."""
        self.video_label.setText(self.tr("Video Feed"))  # Update video label text.
        # Update toggle button text based on current mode.
        self.toggle_mode_btn.setText(self.tr("Switch to Static Mode") if self.toggle_callback.__self__.mode == "live" else self.tr("Switch to Live Mode"))
        self.load_image_btn.setText(self.tr("Load Static Image"))  # Update load button text.
        self.analyze_btn.setText(self.tr("Analyze"))  # Update analyze button text.