# ui/title_bar.py
from PyQt5 import QtWidgets, QtGui, QtCore
import os
import logging

class TitleBar(QtWidgets.QWidget):
    def __init__(self, parent, tr_func):
        super().__init__(parent)
        self.tr = tr_func
        self.setFixedHeight(40)
        self.setStyleSheet("background-color: #2C3E50; border-bottom: 1px solid #3498DB;")
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        
        # Title label
        self.title_label = QtWidgets.QLabel(self.tr("Car Face Tracker"))
        self.title_label.setStyleSheet("font: bold 18px 'Arial'; color: #3498DB; padding: 5px;")
        layout.addWidget(self.title_label)
        
        layout.addStretch()
        
        # Language selection dropdown
        self.language_combo = QtWidgets.QComboBox()
        base_path = os.path.dirname(__file__)
        self.language_combo.addItem(QtGui.QIcon(os.path.join(base_path, "gb.svg")), "en")
        self.language_combo.addItem(QtGui.QIcon(os.path.join(base_path, "fr.svg")), "fr")
        self.language_combo.addItem(QtGui.QIcon(os.path.join(base_path, "de.svg")), "de")
        self.language_combo.addItem(QtGui.QIcon(os.path.join(base_path, "ro.svg")), "ro")
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
        layout.addWidget(self.language_combo)
        logging.debug("TitleBar initialized.")