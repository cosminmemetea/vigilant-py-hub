# ui/main_window.py
# Defines the MainWindow class, the primary PyQt5 window for the Car Face Tracker application.

import cv2  # OpenCV library for video and image processing.
import numpy as np  # Provides array operations for image handling.
from PyQt5 import QtWidgets, QtGui, QtCore  # PyQt5 modules for GUI creation.
import logging  # Facilitates logging for debugging and monitoring.
from ui.title_bar import TitleBar  # Custom title bar with language selector.
from ui.video_panel import VideoPanel  # Panel for video display and controls.
from ui.kpi_panel import TableKpiPanel, StateKpiPanel  # Panels for displaying KPIs.
from ui.translations import translations  # Dictionary of translations for internationalization.
from ui.styles import Styles  # Custom styles for consistent UI appearance.

# Configure logging with timestamp, level, and message format.
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, frame_processor, enabled_kpis):
        """Initialize the MainWindow with video feed, KPI panels, and controls.

        Args:
            frame_processor: Object to process video frames and compute KPIs.
            enabled_kpis: Dictionary mapping KPI groups to their enabled KPI names.
        """
        super().__init__()  # Initialize base QMainWindow class.
        self.current_language = "en"  # Default language for translations.
        self.frame_processor = frame_processor  # Store frame processor for KPI computation.
        self.enabled_kpis = enabled_kpis  # Store enabled KPIs by group.
        self.static_image = None  # Store loaded static image (if any).
        self.mode = "live"  # Current mode: 'live' or 'static'.
        self.cap = None  # Video capture object for live feed.
        self.translations = translations  # Store translation dictionary.
        self.setup_ui()  # Set up the UI components.
        
        # Set up timer for live video updates.
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_live_video)
        if self.mode == "live":
            self.initialize_camera()  # Start camera if in live mode.

    def tr(self, text):
        """Translate text based on the current language.

        Args:
            text: Text to translate.

        Returns:
            str: Translated text or original text if translation is unavailable.
        """
        translated = self.translations.get(self.current_language, {}).get(text, text)
        logging.debug(f"Translating '{text}' to '{translated}' for language '{self.current_language}'")
        return translated
    
    def initialize_camera(self):
        """Initialize or reinitialize the camera for live video feed."""
        if self.cap is not None and self.cap.isOpened():
            self.cap.release()  # Release existing camera if open.
        self.cap = cv2.VideoCapture(0)  # Open default camera (index 0).
        if not self.cap.isOpened():
            logging.error("Could not open camera.")
            QtWidgets.QMessageBox.critical(self, self.tr("Error"), self.tr("Could not access camera."))
            self.mode = "static"  # Switch to static mode on failure.
            self.update_mode_ui()
        else:
            self.timer.start(30)  # Start timer for 30ms intervals (~33 FPS).
            logging.info("Camera initialized successfully.")
    
    def setup_ui(self):
        """Set up the main window's UI layout and components."""
        self.setWindowTitle(self.tr("Car Face Tracker"))  # Set window title.
        self.setMinimumSize(1200, 700)  # Set minimum window size.
        self.setStyleSheet(Styles.MAIN_WINDOW)  # Apply main window styling.
        
        # Create central widget and main layout.
        main_widget = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins.
        
        # Add title bar with language selector.
        self.title_bar = TitleBar(self, lambda x: self.tr(x))  # Pass dynamic translation function.
        self.title_bar.language_combo.currentIndexChanged.connect(self.change_language)
        main_layout.addWidget(self.title_bar)
        
        # Create content area with horizontal layout.
        content_widget = QtWidgets.QWidget()
        content_layout = QtWidgets.QHBoxLayout(content_widget)
        content_layout.setContentsMargins(15, 15, 15, 15)  # Add padding.
        content_layout.setSpacing(20)  # Set spacing between widgets.
        
        # Initialize KPI panels dictionary.
        self.kpi_panels = {}
        # Add state KPI panel if present in enabled KPIs.
        if "state" in self.enabled_kpis:
            state_panel = StateKpiPanel(self.enabled_kpis["state"], lambda x: self.tr(x), "state")
            content_layout.addWidget(state_panel, 1)  # Stretch factor 1.
            self.kpi_panels["state"] = state_panel
        
        # Add video panel for live/static display and controls.
        self.video_panel = VideoPanel(self, lambda x: self.tr(x), self.toggle_mode, self.load_static_image, self.analyze_static_image)
        content_layout.addWidget(self.video_panel, 3)  # Stretch factor 3 for larger video area.
        
        # Create right-side widget for numeric KPI panels.
        right_widget = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(15)
        
        # Add table-based KPI panels for non-state groups.
        for group in self.enabled_kpis.keys() - {"state"}:
            panel = TableKpiPanel(self.enabled_kpis[group], lambda x: self.tr(x), group)
            right_layout.addWidget(panel, 2 if group == "numeric" else 1)  # Larger stretch for numeric.
            self.kpi_panels[group] = panel
        
        content_layout.addWidget(right_widget, 1)  # Stretch factor 1 for right widget.
        
        main_layout.addWidget(content_widget)  # Add content to main layout.
        self.setCentralWidget(main_widget)  # Set main widget as central.
        self.update_mode_ui()  # Update UI based on current mode.
        self.apply_fade_in_animation()  # Apply initial fade-in effect.
    
    def toggle_mode(self):
        """Toggle between live and static modes."""
        if self.mode == "live":
            self.mode = "static"
            self.video_panel.toggle_mode_btn.setText(self.tr("Switch to Live Mode"))
            self.timer.stop()  # Stop live video updates.
            if hasattr(self, 'cap') and self.cap.isOpened():
                self.cap.release()  # Release camera.
                self.cap = None
            logging.info("Switched to static mode.")
        else:
            self.mode = "live"
            self.video_panel.toggle_mode_btn.setText(self.tr("Switch to Static Mode"))
            self.static_image = None  # Clear static image.
            self.video_panel.video_label.setText(self.tr("Video Feed"))  # Reset video label.
            self.initialize_camera()  # Start camera.
            logging.info("Switched to live mode.")
        self.update_mode_ui()  # Update UI for mode change.
    
    def update_mode_ui(self):
        """Update UI elements based on the current mode."""
        self.video_panel.load_image_btn.setEnabled(self.mode == "static")
        self.video_panel.analyze_btn.setEnabled(self.mode == "static")
    
    def update_live_video(self):
        """Update the live video feed and KPI values."""
        if not hasattr(self, 'cap') or not self.cap.isOpened():
            logging.warning("Camera is not open.")
            self.initialize_camera()  # Attempt to reinitialize.
            return
        ret, frame = self.cap.read()  # Read frame from camera.
        if ret:
            results = self.frame_processor.process_frame(frame)  # Process frame for KPIs.
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert to RGB for Qt.
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QtGui.QImage(rgb_frame.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
            self.video_panel.video_label.setPixmap(QtGui.QPixmap.fromImage(qt_image))  # Display frame.
            for panel in self.kpi_panels.values():
                panel.update_values(results)  # Update KPI panels.
            self.video_panel.update_video_style(results)  # Update video style based on results.
        else:
            logging.error("Failed to read frame from camera.")
    
    def load_static_image(self):
        """Load a static image from file for analysis."""
        options = QtWidgets.QFileDialog.Options()
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, self.tr("Load Static Image"), "",
                                                            self.tr("Image Files (*.png *.jpg *.jpeg)"), options=options)
        if filename:
            self.static_image = cv2.imread(filename)  # Load image with OpenCV.
            if self.static_image is None:
                logging.error(f"Could not load image from {filename}")
                QtWidgets.QMessageBox.warning(self, self.tr("Error"), self.tr("Could not load image."))
            else:
                logging.info(f"Image loaded from {filename}")
                rgb_image = cv2.cvtColor(self.static_image, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                qt_image = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
                self.video_panel.video_label.setPixmap(QtGui.QPixmap.fromImage(qt_image))  # Display image.
                for panel in self.kpi_panels.values():
                    panel.update_values({})  # Clear KPI values until analyzed.
    
    def analyze_static_image(self):
        """Analyze the loaded static image and update KPI values."""
        if self.static_image is None:
            QtWidgets.QMessageBox.warning(self, self.tr("No Image"), self.tr("Please load a static image first."))
            return
        logging.info("Analyzing static image...")
        from adapters.mediapipe_adapter import MediaPipeAdapter
        # Reconfigure frame processor for static mode.
        self.frame_processor.mediapipe_adapter = MediaPipeAdapter(mode="static", config={
            "max_num_faces": 1,
            "refine_landmarks": True,
            "min_detection_confidence": 0.5,
            "min_tracking_confidence": 0.5
        })
        results = self.frame_processor.process_frame(self.static_image)  # Process image.
        rgb_image = cv2.cvtColor(self.static_image, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        self.video_panel.video_label.setPixmap(QtGui.QPixmap.fromImage(qt_image))  # Redisplay image.
        for panel in self.kpi_panels.values():
            panel.update_values(results)  # Update KPI panels.
        self.video_panel.update_video_style(results)  # Update video style.
    
    def apply_fade_in_animation(self):
        """Apply a fade-in animation to the window on startup."""
        effect = QtWidgets.QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(effect)
        self.animation = QtCore.QPropertyAnimation(effect, b"opacity")
        self.animation.setDuration(1000)  # 1-second duration.
        self.animation.setStartValue(0)  # Start fully transparent.
        self.animation.setEndValue(1)  # End fully opaque.
        self.animation.start()
    
    def change_language(self, index):
        """Change the application language based on combo box selection.

        Args:
            index: Index of the selected language in the combo box.
        """
        languages = ["en", "fr", "de", "ro"]
        self.current_language = languages[index]
        logging.debug(f"Language changing to {self.current_language}")
        self.retranslate_ui()  # Update all UI text.
        logging.info(f"Language changed to {self.current_language}")
    
    def retranslate_ui(self):
        """Update all UI text with translated strings."""
        self.setWindowTitle(self.tr("Car Face Tracker"))
        self.title_bar.title_label.setText(self.tr("Car Face Tracker"))
        self.video_panel.retranslate_ui()  # Update video panel text.
        for panel in self.kpi_panels.values():
            panel.retranslate_ui()  # Update KPI panel text.
        logging.debug("MainWindow UI retranslated")
    
    def closeEvent(self, event):
        """Handle window close event to clean up resources.

        Args:
            event: QCloseEvent object.
        """
        if hasattr(self, 'timer'):
            self.timer.stop()  # Stop video update timer.
        if hasattr(self, 'cap') and self.cap is not None and self.cap.isOpened():
            self.cap.release()  # Release camera.
            logging.info("Camera released on application close.")
        event.accept()  # Accept the close event.