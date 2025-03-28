# ui/main_window.py
import cv2
import numpy as np
from PyQt5 import QtWidgets, QtGui, QtCore
import logging
from ui.title_bar import TitleBar
from ui.kpi_table import KPITable
from ui.video_panel import VideoPanel

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class MainWindow(QtWidgets.QMainWindow):
    translations = {
        "en": {
            "Car Face Tracker": "Car Face Tracker",
            "KPI": "KPI",
            "Value": "Value",
            "Video Feed": "Video Feed",
            "Switch to Static Mode": "Switch to Static Mode",
            "Switch to Live Mode": "Switch to Live Mode",
            "Load Static Image": "Load Static Image",
            "Analyze": "Analyze",
            "No Image": "No Image",
            "Please load a static image first.": "Please load a static image first.",
            "Yaw": "Yaw",
            "Pitch": "Pitch",
            "Roll": "Roll",
            "Tilt": "Tilt",
            "Yawn": "Yawn",
            "Owl Looking": "Owl Looking",
            "Lizard Looking": "Lizard Looking",
            "Left Eye Openness": "Left Eye Openness",
            "Right Eye Openness": "Right Eye Openness",
            "Adult": "Adult",
            "Belt": "Belt",
            "Distraction": "Distraction",
            "Image Files (*.png *.jpg *.jpeg)": "Image Files (*.png *.jpg *.jpeg)",
            "Error": "Error",
            "Could not access camera.": "Could not access camera.",
            "Could not load image.": "Could not load image."
        },
        "fr": {
            "Car Face Tracker": "Suivi de Visage en Voiture",
            "KPI": "Indicateur",
            "Value": "Valeur",
            "Video Feed": "Flux Vidéo",
            "Switch to Static Mode": "Passer en Mode Statique",
            "Switch to Live Mode": "Passer en Mode Live",
            "Load Static Image": "Charger une Image Statique",
            "Analyze": "Analyser",
            "No Image": "Pas d'Image",
            "Please load a static image first.": "Veuillez d'abord charger une image statique.",
            "Yaw": "Lacet",
            "Pitch": "Tangage",
            "Roll": "Roulis",
            "Tilt": "Inclinaison",
            "Yawn": "Bâillement",
            "Owl Looking": "Regard Chouette",
            "Lizard Looking": "Regard Lézard",
            "Left Eye Openness": "Ouverture Oeil Gauche",
            "Right Eye Openness": "Ouverture Oeil Droit",
            "Adult": "Adulte",
            "Belt": "Ceinture",
            "Distraction": "Distraction",
            "Image Files (*.png *.jpg *.jpeg)": "Fichiers Image (*.png *.jpg *.jpeg)",
            "Error": "Erreur",
            "Could not access camera.": "Impossible d'accéder à la caméra.",
            "Could not load image.": "Impossible de charger l'image."
        },
        "de": {
            "Car Face Tracker": "Autogesichtserkennung",
            "KPI": "KPI",
            "Value": "Wert",
            "Video Feed": "Videostream",
            "Switch to Static Mode": "Zum Statischen Modus Wechseln",
            "Switch to Live Mode": "Zum Live-Modus Wechseln",
            "Load Static Image": "Statisches Bild Laden",
            "Analyze": "Analysieren",
            "No Image": "Kein Bild",
            "Please load a static image first.": "Bitte laden Sie zuerst ein statisches Bild.",
            "Yaw": "Gieren",
            "Pitch": "Nicken",
            "Roll": "Rollen",
            "Tilt": "Neigung",
            "Yawn": "Gähnen",
            "Owl Looking": "Eulenblick",
            "Lizard Looking": "Echsenblick",
            "Left Eye Openness": "Linkes Auge Offenheit",
            "Right Eye Openness": "Rechtes Auge Offenheit",
            "Adult": "Erwachsener",
            "Belt": "Gurt",
            "Distraction": "Ablenkung",
            "Image Files (*.png *.jpg *.jpeg)": "Bilddateien (*.png *.jpg *.jpeg)",
            "Error": "Fehler",
            "Could not access camera.": "Kamera konnte nicht aufgerufen werden.",
            "Could not load image.": "Bild konnte nicht geladen werden."
        },
        "ro": {
            "Car Face Tracker": "Urmărire Facială Auto",
            "KPI": "KPI",
            "Value": "Valoare",
            "Video Feed": "Flux Video",
            "Switch to Static Mode": "Trece la Modul Static",
            "Switch to Live Mode": "Trece la Modul Live",
            "Load Static Image": "Încarcă Imagine Statică",
            "Analyze": "Analizează",
            "No Image": "Fără Imagine",
            "Please load a static image first.": "Încarcă mai întâi o imagine statică.",
            "Yaw": "Gir",
            "Pitch": "Tangaj",
            "Roll": "Ruliu",
            "Tilt": "Înclinare",
            "Yawn": "Căscat",
            "Owl Looking": "Privire Bufniță",
            "Lizard Looking": "Privire Șopârlă",
            "Left Eye Openness": "Deschidere Ochi Stâng",
            "Right Eye Openness": "Deschidere Ochi Drept",
            "Adult": "Adult",
            "Belt": "Centură",
            "Distraction": "Distragere",
            "Image Files (*.png *.jpg *.jpeg)": "Fișiere Imagine (*.png *.jpg *.jpeg)",
            "Error": "Eroare",
            "Could not access camera.": "Nu s-a putut accesa camera.",
            "Could not load image.": "Nu s-a putut încărca imaginea."
        }
    }

    def __init__(self, frame_processor):
        super().__init__()
        self.current_language = "en"  # Default language
        self.frame_processor = frame_processor
        self.static_image = None  # Placeholder for static image
        self.mode = "live"  # Start in live mode
        self.cap = None  # Camera object, initialized later
        
        # Set up the UI
        self.setup_ui()
        
        # Set up a timer for live video updates
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_live_video)
        if self.mode == "live":
            self.initialize_camera()

    def tr(self, text):
        # Translate text based on the current language
        return self.translations.get(self.current_language, {}).get(text, text)
    
    def initialize_camera(self):
        # Initialize or reinitialize the camera for live mode
        if self.cap is not None and self.cap.isOpened():
            self.cap.release()
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            logging.error("Could not open camera.")
            QtWidgets.QMessageBox.critical(self, self.tr("Error"), self.tr("Could not access camera."))
            self.mode = "static"
            self.update_mode_ui()
        else:
            self.timer.start(30)  # Update every 30ms (~33 FPS)
            logging.info("Camera initialized successfully.")
    
    def setup_ui(self):
        # Set up the user interface in a modular way
        self.setWindowTitle(self.tr("Car Face Tracker"))
        self.setMinimumSize(1200, 700)
        
        # Main widget and layout
        main_widget = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add title bar
        self.title_bar = TitleBar(self, self.tr)
        self.title_bar.language_combo.currentIndexChanged.connect(self.change_language)
        main_layout.addWidget(self.title_bar)
        
        # Content widget and layout
        content_widget = QtWidgets.QWidget()
        content_layout = QtWidgets.QHBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(30)
        
        # Left KPI table (expanded for new KPIs)
        self.left_table = KPITable(9, ["Yaw", "Pitch", "Roll", "Tilt", "Yawn", "Owl Looking", "Lizard Looking", 
                                      "Left Eye Openness", "Right Eye Openness"], self.tr)
        content_layout.addWidget(self.left_table, 1)
        
        # Center panel: Video feed and controls (removed toggle annotations button)
        self.video_panel = VideoPanel(self, self.tr, self.toggle_mode, self.load_static_image, 
                                      self.analyze_static_image)
        content_layout.addWidget(self.video_panel, 2)
        
        # Right KPI table
        self.right_table = KPITable(3, ["Adult", "Belt", "Distraction"], self.tr)
        content_layout.addWidget(self.right_table, 1)
        
        main_layout.addWidget(content_widget)
        self.setCentralWidget(main_widget)
        self.setStyleSheet("background-color: #1A252F;")
        
        self.update_mode_ui()
        self.apply_fade_in_animation()
    
    def toggle_mode(self):
        # Switch between live and static modes
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
        # Update button states based on the current mode
        self.video_panel.load_image_btn.setEnabled(self.mode == "static")
        self.video_panel.analyze_btn.setEnabled(self.mode == "static")
    
    def update_live_video(self):
        # Update the live video feed with markers
        if not hasattr(self, 'cap') or not self.cap.isOpened():
            logging.warning("Camera is not open.")
            self.initialize_camera()
            return
        ret, frame = self.cap.read()
        if ret:
            logging.debug(f"Frame received: {frame.shape}")
            # Process the frame and apply markers
            results = self.frame_processor.process_frame(frame)
            logging.debug(f"Live video results: {results}")
            # Convert the processed frame to RGB for display
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QtGui.QImage(rgb_frame.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
            self.video_panel.video_label.setPixmap(QtGui.QPixmap.fromImage(qt_image))
            self.update_kpis(results)
        else:
            logging.error("Failed to read frame from camera.")
    
    def load_static_image(self):
        # Load a static image from file
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
                self.update_kpis({})  # Reset KPIs
    
    def analyze_static_image(self):
        # Analyze the static image and display with markers
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
    
    def update_kpis(self, results):
        # Update KPI values in the tables
        kpi_keys_left = ["yaw", "pitch", "roll", "tilt", "yawn", "owl_looking", "lizard_looking", 
                         "left_eye_openness", "right_eye_openness"]
        for i, key in enumerate(kpi_keys_left):
           
            value = results.get(key, "N/A")
            if isinstance(value, (int, float)):
                value = f"{value:.2f}"  # Increased precision for openness
            elif value is None:
                value = "N/A"
            self.left_table.item(i, 1).setText(str(value))
            logging.debug(f"Updated KPI {key}: {value}")
        
        kpi_keys_right = ["adult", "belt", "distraction"]
        for i, key in enumerate(kpi_keys_right):
            value = results.get(key, "N/A")
            self.right_table.item(i, 1).setText(str(value))
            logging.debug(f"Updated KPI {key}: {value}")
    
    def apply_fade_in_animation(self):
        # Apply a fade-in animation when the window opens
        effect = QtWidgets.QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(effect)
        self.animation = QtCore.QPropertyAnimation(effect, b"opacity")
        self.animation.setDuration(1000)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()
    
    def change_language(self, index):
        # Change the language and update the UI
        languages = ["en", "fr", "de", "ro"]
        self.current_language = languages[index]
        self.retranslate_ui()
        logging.info(f"Language changed to {self.current_language}")
    
    def retranslate_ui(self):
        # Refresh UI text with the current language
        self.setWindowTitle(self.tr("Car Face Tracker"))
        self.title_bar.title_label.setText(self.tr("Car Face Tracker"))
        self.left_table.setHorizontalHeaderLabels([self.tr("KPI"), self.tr("Value")])
        self.right_table.setHorizontalHeaderLabels([self.tr("KPI"), self.tr("Value")])
        self.video_panel.video_label.setText(self.tr("Video Feed"))
        self.video_panel.toggle_mode_btn.setText(self.tr("Switch to Static Mode") if self.mode == "live" else self.tr("Switch to Live Mode"))
        self.video_panel.load_image_btn.setText(self.tr("Load Static Image"))
        self.video_panel.analyze_btn.setText(self.tr("Analyze"))
        kpi_keys_left = ["Yaw", "Pitch", "Roll", "Tilt", "Yawn", "Owl Looking", "Lizard Looking", 
                         "Left Eye Openness", "Right Eye Openness"]
        for i, kpi in enumerate(kpi_keys_left):
            self.left_table.item(i, 0).setText(self.tr(kpi))
        kpi_keys_right = ["Adult", "Belt", "Distraction"]
        for i, kpi in enumerate(kpi_keys_right):
            self.right_table.item(i, 0).setText(self.tr(kpi))
        logging.debug("UI retranslated.")
    
    def closeEvent(self, event):
        # Release resources when closing the window
        if hasattr(self, 'timer'):
            self.timer.stop()
        if hasattr(self, 'cap') and self.cap is not None and self.cap.isOpened():
            self.cap.release()
            logging.info("Camera released on application close.")
        event.accept()