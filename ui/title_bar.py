from PyQt5 import QtWidgets, QtGui, QtCore
import os
import logging
from ui.styles import Styles

class TitleBar(QtWidgets.QWidget):
    def __init__(self, parent, tr_func):
        super().__init__(parent)
        self.tr = tr_func
        self.setFixedHeight(40)
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        
        # Title label
        self.title_label = QtWidgets.QLabel(self.tr("Car Face Tracker"))
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
        layout.addWidget(self.language_combo)
        
        # Apply styles
        self.setStyleSheet(Styles.TITLE_BAR)
        self.title_label.setStyleSheet(Styles.TITLE_LABEL)
        self.language_combo.setStyleSheet(Styles.LANGUAGE_COMBO)
        
        logging.debug("TitleBar initialized.")