import cv2
import numpy as np
from PyQt5 import QtWidgets, QtGui, QtCore
import logging
from ui.title_bar import TitleBar
from ui.kpi_table import KPITable
from ui.video_panel import VideoPanel
from ui.state_panel import StatePanel

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
            "Left Eye Openness": "Left Eye Openness",
            "Right Eye Openness": "Right Eye Openness",
            "Adult": "Adult",
            "Belt": "Belt",
            "Inattention": "Inattention",
            "Fatigue": "Fatigue",
            "Microsleep": "Microsleep",
            "Sleep": "Sleep",
            "Unresponsive": "Unresponsive",
            "Drowsiness": "Drowsiness",
            "None": "None",
            "Pending": "Pending",
            "Detected": "Detected",
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
            "Left Eye Openness": "Ouverture Œil Gauche",
            "Right Eye Openness": "Ouverture Œil Droit",
            "Adult": "Adulte",
            "Belt": "Ceinture",
            "Inattention": "Inattention",
            "Fatigue": "Fatigue",
            "Microsleep": "Microsommeil",
            "Sleep": "Sommeil",
            "Unresponsive": "Non Réactif",
            "Drowsiness": "Somnolence",
            "None": "Aucun",
            "Pending": "En Attente",
            "Detected": "Détecté",
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
            "Left Eye Openness": "Linkes Auge Offenheit",
            "Right Eye Openness": "Rechtes Auge Offenheit",
            "Adult": "Erwachsener",
            "Belt": "Gurt",
            "Inattention": "Unaufmerksamkeit",
            "Fatigue": "Müdigkeit",
            "Microsleep": "Mikroschlaf",
            "Sleep": "Schlaf",
            "Unresponsive": "Nicht Ansprechbar",
            "Drowsiness": "Schläfrigkeit",
            "None": "Kein",
            "Pending": "Ausstehend",
            "Detected": "Erkannt",
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
            "Left Eye Openness": "Deschidere Ochi Stâng",
            "Right Eye Openness": "Deschidere Ochi Drept",
            "Adult": "Adult",
            "Belt": "Centură",
            "Inattention": "Neatenție",
            "Fatigue": "Oboseală",
            "Microsleep": "Microsomn",
            "Sleep": "Somn",
            "Unresponsive": "Nereceptiv",
            "Drowsiness": "Somnolență",
            "None": "Niciunul",
            "Pending": "În Așteptare",
            "Detected": "Detectat",
            "Image Files (*.png *.jpg *.jpeg)": "Fișiere Imagine (*.png *.jpg *.jpeg)",
            "Error": "Eroare",
            "Could not access camera.": "Nu s-a putut accesa camera.",
            "Could not load image.": "Nu s-a putut încărca imaginea."
        }
    }

    def __init__(self, frame_processor, enabled_kpis):
        super().__init__()
        self.current_language = "en"
        self.frame_processor = frame_processor
        self.enabled_kpis = enabled_kpis
        self.static_image = None
        self.mode = "live"
        self.cap = None
        
        self.setup_ui()
        
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_live_video)
        if self.mode == "live":
            self.initialize_camera()

    def tr(self, text):
        return self.translations.get(self.current_language, {}).get(text, text)
    
    def initialize_camera(self):
        if self.cap is not None and self.cap.isOpened():
            self.cap.release()
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            logging.error("Could not open camera.")
            QtWidgets.QMessageBox.critical(self, self.tr("Error"), self.tr("Could not access camera."))
            self.mode = "static"
            self.update_mode_ui()
        else:
            self.timer.start(30)
            logging.info("Camera initialized successfully.")
    
    def setup_ui(self):
        self.setWindowTitle(self.tr("Car Face Tracker"))
        self.setMinimumSize(1200, 700)
        
        main_widget = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Title bar
        self.title_bar = TitleBar(self, self.tr)
        self.title_bar.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2E2E2E, stop:1 #1A1A1A);
            border-bottom: 1px solid #444444;
        """)
        self.title_bar.language_combo.currentIndexChanged.connect(self.change_language)
        main_layout.addWidget(self.title_bar)
        
        # Main content layout
        content_widget = QtWidgets.QWidget()
        content_layout = QtWidgets.QHBoxLayout(content_widget)
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.setSpacing(20)
        
        # Left Section: State KPIs
        left_widget = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        state_kpis = self.enabled_kpis.get("state", [])
        self.state_panel = StatePanel(state_kpis, self.tr)
        left_layout.addWidget(self.state_panel)
        left_layout.addStretch()
        content_layout.addWidget(left_widget, 1)
        
        # Center Section: Video Panel
        self.video_panel = VideoPanel(self, self.tr, self.toggle_mode, self.load_static_image, 
                                      self.analyze_static_image)
        content_layout.addWidget(self.video_panel, 3)
        
        # Right Section: Numeric and Binary KPIs
        right_widget = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(15)
        
        # Top Right: Numeric KPIs
        numeric_kpis = self.enabled_kpis.get("numeric", [])
        kpi_labels = [self.tr(kpi.capitalize().replace("_", " ")) for kpi in numeric_kpis]
        self.numeric_table = KPITable(len(kpi_labels), kpi_labels, self.tr)
        self.numeric_table.setStyleSheet("""
            QTableWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2E2E2E, stop:1 #1A1A1A);
                border: 1px solid #444444;
                border-radius: 8px;
                font: 13px "Arial";
                color: #D3D3D3;
            }
            QHeaderView::section {
                background: #3498DB;
                color: white;
                padding: 5px;
                border: none;
                font: bold 14px;
            }
        """)
        right_layout.addWidget(self.numeric_table, 2)
        
        # Bottom Right: Binary KPIs
        binary_kpis = self.enabled_kpis.get("binary", [])
        binary_labels = [self.tr(kpi.capitalize().replace("_", " ")) for kpi in binary_kpis]
        self.binary_table = KPITable(len(binary_labels), binary_labels, self.tr)
        self.binary_table.setStyleSheet("""
            QTableWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2E2E2E, stop:1 #1A1A1A);
                border: 1px solid #444444;
                border-radius: 8px;
                font: 13px "Arial";
                color: #D3D3D3;
            }
            QHeaderView::section {
                background: #3498DB;
                color: white;
                padding: 5px;
                border: none;
                font: bold 14px;
            }
        """)
        right_layout.addWidget(self.binary_table, 1)
        
        content_layout.addWidget(right_widget, 1)
        
        main_layout.addWidget(content_widget)
        self.setCentralWidget(main_widget)
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #333333, stop:1 #1F1F1F);
            }
        """)
        
        self.update_mode_ui()
        self.apply_fade_in_animation()
    
    def toggle_mode(self):
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
        self.video_panel.load_image_btn.setEnabled(self.mode == "static")
        self.video_panel.analyze_btn.setEnabled(self.mode == "static")
    
    def update_live_video(self):
        if not hasattr(self, 'cap') or not self.cap.isOpened():
            logging.warning("Camera is not open.")
            self.initialize_camera()
            return
        ret, frame = self.cap.read()
        if ret:
            logging.debug(f"Frame received: {frame.shape}")
            results = self.frame_processor.process_frame(frame)
            logging.debug(f"Live video results: {results}")
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QtGui.QImage(rgb_frame.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
            self.video_panel.video_label.setPixmap(QtGui.QPixmap.fromImage(qt_image))
            self.update_kpis(results)
            self.state_panel.update_states(results)
            self.video_panel.update_video_style(results)
        else:
            logging.error("Failed to read frame from camera.")
    
    def load_static_image(self):
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
                self.update_kpis({})
                self.state_panel.update_states({})
    
    def analyze_static_image(self):
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
        self.state_panel.update_states(results)
        self.video_panel.update_video_style(results)
    
    def update_kpis(self, results):
        # Numeric KPIs (Top Right Table)
        for i, key in enumerate(self.enabled_kpis.get("numeric", [])):
            value = results.get(key, "N/A")
            if isinstance(value, (int, float)):
                value = f"{value:.2f}"
            elif value is None:
                value = "N/A"
            item = self.numeric_table.item(i, 1)
            if item is None:
                item = QtWidgets.QTableWidgetItem("N/A")
                item.setForeground(QtGui.QColor("white"))
                item.setFlags(QtCore.Qt.ItemIsEnabled)
                self.numeric_table.setItem(i, 1, item)
                logging.warning(f"Reinitialized missing item at numeric table row {i}, column 1")
            item.setText(str(value))
            logging.debug(f"Updated numeric KPI {key}: {value}")
        
        # Binary KPIs (Bottom Right Table)
        for i, key in enumerate(self.enabled_kpis.get("binary", [])):
            value = results.get(key, "N/A")
            item = self.binary_table.item(i, 1)
            if item is None:
                item = QtWidgets.QTableWidgetItem("N/A")
                item.setForeground(QtGui.QColor("white"))
                item.setFlags(QtCore.Qt.ItemIsEnabled)
                self.binary_table.setItem(i, 1, item)
                logging.warning(f"Reinitialized missing item at binary table row {i}, column 1")
            item.setText(str(value))
            logging.debug(f"Updated binary KPI {key}: {value}")
    
    def apply_fade_in_animation(self):
        effect = QtWidgets.QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(effect)
        self.animation = QtCore.QPropertyAnimation(effect, b"opacity")
        self.animation.setDuration(1000)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()
    
    def change_language(self, index):
        languages = ["en", "fr", "de", "ro"]
        self.current_language = languages[index]
        self.retranslate_ui()
        logging.info(f"Language changed to {self.current_language}")
    
    def retranslate_ui(self):
        self.setWindowTitle(self.tr("Car Face Tracker"))
        self.title_bar.title_label.setText(self.tr("Car Face Tracker"))
        self.numeric_table.setHorizontalHeaderLabels([self.tr("KPI"), self.tr("Value")])
        self.binary_table.setHorizontalHeaderLabels([self.tr("KPI"), self.tr("Value")])
        self.video_panel.video_label.setText(self.tr("Video Feed"))
        self.video_panel.toggle_mode_btn.setText(self.tr("Switch to Static Mode") if self.mode == "live" else self.tr("Switch to Live Mode"))
        self.video_panel.load_image_btn.setText(self.tr("Load Static Image"))
        self.video_panel.analyze_btn.setText(self.tr("Analyze"))
        
        for i, kpi in enumerate(self.enabled_kpis.get("numeric", [])):
            label = kpi.capitalize().replace("_", " ")
            self.numeric_table.item(i, 0).setText(self.tr(label))
        
        for i, kpi in enumerate(self.enabled_kpis.get("binary", [])):
            label = kpi.capitalize().replace("_", " ")
            self.binary_table.item(i, 0).setText(self.tr(label))
        
        self.state_panel.retranslate_ui()  # Update state panel translations
        logging.debug("UI retranslated.")
    
    def closeEvent(self, event):
        if hasattr(self, 'timer'):
            self.timer.stop()
        if hasattr(self, 'cap') and self.cap is not None and self.cap.isOpened():
            self.cap.release()
            logging.info("Camera released on application close.")
        event.accept()