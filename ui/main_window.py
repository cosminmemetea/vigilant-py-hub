# ui/main_window.py
import cv2
import numpy as np
from PyQt5 import QtWidgets, QtGui, QtCore
import os

class MainWindow(QtWidgets.QMainWindow):
    translations = {
        "en": {
            "Car Face Tracker": "hera",
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
            "Adult": "Adult",
            "Belt": "Belt",
            "Image Files (*.png *.jpg *.jpeg)": "Image Files (*.png *.jpg *.jpeg)"
        },
        "fr": {
            "Car Face Tracker": "hera",
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
            "Adult": "Adulte",
            "Belt": "Ceinture",
            "Image Files (*.png *.jpg *.jpeg)": "Fichiers Image (*.png *.jpg *.jpeg)"
        },
        "de": {
            "Car Face Tracker": "hera",
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
            "Adult": "Erwachsener",
            "Belt": "Gurt",
            "Image Files (*.png *.jpg *.jpeg)": "Bilddateien (*.png *.jpg *.jpeg)"
        },
        "ro": {  # Adăugăm traduceri pentru română
            "Car Face Tracker": "hera",
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
            "Adult": "Adult",
            "Belt": "Centură",
            "Image Files (*.png *.jpg *.jpeg)": "Fișiere Imagine (*.png *.jpg *.jpeg)"
        }
    }

    def __init__(self, frame_processor):
        super().__init__()
        self.current_language = "en"
        self.frame_processor = frame_processor
        self.static_image = None
        self.mode = "live"
        
        self.setup_ui()
        
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_live_video)
        if self.mode == "live":
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                print("Error: Could not open camera")
            self.timer.start(30)
    
    def setup_ui(self):
        self.setWindowTitle(self.tr("Car Face Tracker"))
        self.setMinimumSize(1200, 700)
        
        # Custom title bar
        title_bar = QtWidgets.QWidget()
        title_bar.setFixedHeight(40)
        title_bar.setStyleSheet("background-color: #2C3E50; border-bottom: 1px solid #3498DB;")
        title_layout = QtWidgets.QHBoxLayout(title_bar)
        title_layout.setContentsMargins(10, 0, 10, 0)
        
        # Titlu "hera"
        title_label = QtWidgets.QLabel(self.tr("Car Face Tracker"))
        title_label.setStyleSheet("""
            font: bold 18px 'Arial';
            color: #3498DB;
            padding: 5px;
        """)
        title_layout.addWidget(title_label)
        
        title_layout.addStretch()
        
        # Language selection dropdown cu SVG-uri
        self.language_combo = QtWidgets.QComboBox()
        base_path = os.path.dirname(__file__)  # Calea către folderul ui
        self.language_combo.addItem(QtGui.QIcon(os.path.join(base_path, "gb.svg")), "")
        self.language_combo.addItem(QtGui.QIcon(os.path.join(base_path, "fr.svg")), "")
        self.language_combo.addItem(QtGui.QIcon(os.path.join(base_path, "de.svg")), "")
        self.language_combo.addItem(QtGui.QIcon(os.path.join(base_path, "ro.svg")), "")
        self.language_combo.setFixedSize(80, 35)
        self.language_combo.setStyleSheet("""
            QComboBox {
                background-color: #3498DB;
                border: 2px solid #FFFFFF;
                border-radius: 8px;
                padding: 5px;
            }
            QComboBox:hover {
                background-color: #2980B9;
            }
            QComboBox::drop-down {
                width: 20px;
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #2C3E50;
                color: white;
                selection-background-color: #3498DB;
                border: 1px solid #FFFFFF;
                min-width: 80px;
                min-height: 40px;
            }
        """)
        self.language_combo.currentIndexChanged.connect(self.change_language)
        title_layout.addWidget(self.language_combo)
        
        # Main widget and layout
        main_widget = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(title_bar)
        
        content_widget = QtWidgets.QWidget()
        content_layout = QtWidgets.QHBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(30)
        
        # Left Panel: KPI Table for Left KPIs
        self.left_table = QtWidgets.QTableWidget(5, 2)
        self.left_table.setHorizontalHeaderLabels([self.tr("KPI"), self.tr("Value")])
        self.left_table.verticalHeader().setVisible(False)
        self.left_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        kpis_left = ["Yaw", "Pitch", "Roll", "Tilt", "Yawn"]
        for i, kpi in enumerate(kpis_left):
            kpi_item = QtWidgets.QTableWidgetItem(self.tr(kpi))
            kpi_item.setForeground(QtGui.QColor("white"))
            kpi_item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.left_table.setItem(i, 0, kpi_item)
            value_item = QtWidgets.QTableWidgetItem("N/A")
            value_item.setForeground(QtGui.QColor("white"))
            value_item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.left_table.setItem(i, 1, value_item)
        self.left_table.setStyleSheet("""
            QTableWidget {
                background-color: #1A252F;
                gridline-color: #3498DB;
                font: bold 14px;
                color: white;
                border-radius: 8px;
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #3498DB;
                padding: 4px;
                border: none;
            }
        """)
        content_layout.addWidget(self.left_table, 1)
        
        # Center Panel: Video Feed and Control Buttons
        center_widget = QtWidgets.QWidget()
        center_layout = QtWidgets.QVBoxLayout(center_widget)
        center_layout.setSpacing(20)
        center_layout.setContentsMargins(0, 0, 0, 0)
        
        self.video_label = QtWidgets.QLabel(self.tr("Video Feed"))
        self.video_label.setAlignment(QtCore.Qt.AlignCenter)
        self.video_label.setFixedSize(800, 600)
        self.video_label.setStyleSheet("""
            background-color: black;
            border: 2px solid #3498DB;
            border-radius: 10px;
            font: bold 16px;
            color: white;
        """)
        center_layout.addWidget(self.video_label, alignment=QtCore.Qt.AlignCenter)
        
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.setSpacing(15)
        
        self.toggle_mode_btn = QtWidgets.QPushButton(self.tr("Switch to Static Mode"))
        self.toggle_mode_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                border-radius: 8px;
                padding: 10px 20px;
                font: bold 12px;
                color: white;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
        """)
        self.toggle_mode_btn.clicked.connect(self.toggle_mode)
        btn_layout.addWidget(self.toggle_mode_btn)
        
        self.load_image_btn = QtWidgets.QPushButton(self.tr("Load Static Image"))
        self.load_image_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                border-radius: 8px;
                padding: 10px 20px;
                font: bold 12px;
                color: white;
            }
            QPushButton:disabled {
                background-color: #7F8C8D;
            }
            QPushButton:hover:enabled {
                background-color: #2980B9;
            }
        """)
        self.load_image_btn.clicked.connect(self.load_static_image)
        btn_layout.addWidget(self.load_image_btn)
        
        self.analyze_btn = QtWidgets.QPushButton(self.tr("Analyze"))
        self.analyze_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ECC71;
                border-radius: 8px;
                padding: 10px 20px;
                font: bold 12px;
                color: white;
            }
            QPushButton:disabled {
                background-color: #7F8C8D;
            }
            QPushButton:hover:enabled {
                background-color: #27AE60;
            }
        """)
        self.analyze_btn.clicked.connect(self.analyze_static_image)
        btn_layout.addWidget(self.analyze_btn)
        
        center_layout.addLayout(btn_layout)
        content_layout.addWidget(center_widget, 2)
        
        # Right Panel: KPI Table for Right KPIs
        self.right_table = QtWidgets.QTableWidget(2, 2)
        self.right_table.setHorizontalHeaderLabels([self.tr("KPI"), self.tr("Value")])
        self.right_table.verticalHeader().setVisible(False)
        self.right_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        kpis_right = ["Adult", "Belt"]
        for i, kpi in enumerate(kpis_right):
            kpi_item = QtWidgets.QTableWidgetItem(self.tr(kpi))
            kpi_item.setForeground(QtGui.QColor("white"))
            kpi_item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.right_table.setItem(i, 0, kpi_item)
            value_item = QtWidgets.QTableWidgetItem("N/A")
            value_item.setForeground(QtGui.QColor("white"))
            value_item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.right_table.setItem(i, 1, value_item)
        self.right_table.setStyleSheet("""
            QTableWidget {
                background-color: #1A252F;
                gridline-color: #3498DB;
                font: bold 14px;
                color: white;
                border-radius: 8px;
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #3498DB;
                padding: 4px;
                border: none;
            }
        """)
        content_layout.addWidget(self.right_table, 1)
        
        main_layout.addWidget(content_widget)
        self.setCentralWidget(main_widget)
        self.setStyleSheet("background-color: #1A252F;")
        
        self.update_mode_ui()
        self.apply_fade_in_animation()
    
    def tr(self, text):
        return self.translations[self.current_language].get(text, text)
    
    def toggle_mode(self):
        if self.mode == "live":
            self.mode = "static"
            self.toggle_mode_btn.setText(self.tr("Switch to Live Mode"))
            self.timer.stop()
            if hasattr(self, 'cap') and self.cap.isOpened():
                self.cap.release()
        else:
            self.mode = "live"
            self.toggle_mode_btn.setText(self.tr("Switch to Static Mode"))
            self.static_image = None
            self.video_label.setText(self.tr("Video Feed"))
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                print("Error: Could not reopen camera")
            self.timer.start(30)
        self.update_mode_ui()
    
    def update_mode_ui(self):
        if self.mode == "live":
            self.load_image_btn.setEnabled(False)
            self.analyze_btn.setEnabled(False)
        else:
            self.load_image_btn.setEnabled(True)
            self.analyze_btn.setEnabled(True)
    
    def update_live_video(self):
        if not hasattr(self, 'cap') or not self.cap.isOpened():
            print("Camera not opened")
            return
        ret, frame = self.cap.read()
        if ret:
            print("Frame captured successfully")
            results = self.frame_processor.process_frame(frame)
            print(f"Live video results: {results}")
            self.update_kpis(results)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QtGui.QImage(rgb_frame.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
            self.video_label.setPixmap(QtGui.QPixmap.fromImage(qt_image))
        else:
            print("Failed to capture frame")
    
    def load_static_image(self):
        options = QtWidgets.QFileDialog.Options()
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, self.tr("Load Static Image"), "",
                                                            self.tr("Image Files (*.png *.jpg *.jpeg)"), options=options)
        if filename:
            self.static_image = cv2.imread(filename)
            if self.static_image is None:
                print(f"Error: Could not load image from {filename}")
            else:
                print(f"Loaded image from {filename}")
                rgb_image = cv2.cvtColor(self.static_image, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                qt_image = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
                self.video_label.setPixmap(QtGui.QPixmap.fromImage(qt_image))
                self.update_kpis({})  # Reset KPIs
    
    def analyze_static_image(self):
        if self.static_image is None:
            QtWidgets.QMessageBox.warning(self, self.tr("No Image"), self.tr("Please load a static image first."))
            return
        print("Analyzing static image...")
        # Reinitialize MediaPipeAdapter to avoid the persistant state.
        from adapters.mediapipe_adapter import MediaPipeAdapter
        self.frame_processor.mediapipe_adapter = MediaPipeAdapter(mode="static", config={
            "max_num_faces": 1,
            "refine_landmarks": True,
            "min_detection_confidence": 0.5,
            "min_tracking_confidence": 0.5
        })
        results = self.frame_processor.process_frame(self.static_image)
        print(f"Analysis results: {results}")
        self.update_kpis(results)
    
    def update_kpis(self, results):
        kpi_keys_left = ["yaw", "pitch", "roll", "tilt", "yawn"]
        for i, key in enumerate(kpi_keys_left):
            value = results.get(key, "N/A")
            if isinstance(value, (int, float)):
                value = f"{value:.1f}"
            elif value is None:
                value = "N/A"
            self.left_table.item(i, 1).setText(str(value))
        
        kpi_keys_right = ["adult", "belt"]
        for i, key in enumerate(kpi_keys_right):
            value = results.get(key, "N/A")
            self.right_table.item(i, 1).setText(str(value))
    
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
    
    def retranslate_ui(self):
        self.setWindowTitle(self.tr("Car Face Tracker"))
        self.left_table.setHorizontalHeaderLabels([self.tr("KPI"), self.tr("Value")])
        self.right_table.setHorizontalHeaderLabels([self.tr("KPI"), self.tr("Value")])
        self.video_label.setText(self.tr("Video Feed"))
        self.toggle_mode_btn.setText(self.tr("Switch to Static Mode") if self.mode == "live" else self.tr("Switch to Live Mode"))
        self.load_image_btn.setText(self.tr("Load Static Image"))
        self.analyze_btn.setText(self.tr("Analyze"))
        for i, kpi in enumerate(["Yaw", "Pitch", "Roll", "Tilt", "Yawn"]):
            self.left_table.item(i, 0).setText(self.tr(kpi))
        for i, kpi in enumerate(["Adult", "Belt"]):
            self.right_table.item(i, 0).setText(self.tr(kpi))
    
    def closeEvent(self, event):
        if hasattr(self, 'timer'):
            self.timer.stop()
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()
        event.accept()