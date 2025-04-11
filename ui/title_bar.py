# ui/title_bar.py
# Defines the TitleBar class, a PyQt5 widget for displaying the application title and language selector.

from PyQt5 import QtWidgets, QtGui, QtCore  # PyQt5 modules for creating GUI components.
import os  # Provides utilities for file and directory path operations.
import logging  # Facilitates logging for debugging and monitoring UI initialization.
from ui.styles import Styles  # Custom styles for consistent UI appearance.

class TitleBar(QtWidgets.QWidget):
    def __init__(self, parent, tr_func):
        """Initialize the TitleBar with a title label and language selector.

        Args:
            parent: Parent widget for this title bar.
            tr_func: Translation function for internationalization.
        """
        super().__init__(parent)  # Initialize base QWidget class.
        self.tr = tr_func  # Store translation function for dynamic text updates.
        self.setFixedHeight(40)  # Set fixed height for the title bar.
        layout = QtWidgets.QHBoxLayout(self)  # Create horizontal layout for components.
        layout.setContentsMargins(10, 0, 10, 0)  # Set margins for padding.
        
        # Create label to display the application title.
        self.title_label = QtWidgets.QLabel(self.tr("Car Face Tracker"))
        layout.addWidget(self.title_label)  # Add title to layout.
        
        layout.addStretch()  # Add stretchable space to push language selector to the right.
        
        # Create combo box for language selection with flag icons.
        self.language_combo = QtWidgets.QComboBox()
        # Construct path to flag icons relative to this file's directory.
        base_path = os.path.join(os.path.dirname(__file__), 'flags')
        # Add language options with corresponding flag icons.
        self.language_combo.addItem(QtGui.QIcon(os.path.join(base_path, "gb.svg")), "en")
        self.language_combo.addItem(QtGui.QIcon(os.path.join(base_path, "fr.svg")), "fr")
        self.language_combo.addItem(QtGui.QIcon(os.path.join(base_path, "de.svg")), "de")
        self.language_combo.addItem(QtGui.QIcon(os.path.join(base_path, "ro.svg")), "ro")
        self.language_combo.setFixedSize(80, 35)  # Set fixed size for the combo box.
        layout.addWidget(self.language_combo)  # Add combo box to layout.
        
        # Apply custom styles to the title bar and its components.
        self.setStyleSheet(Styles.TITLE_BAR)
        self.title_label.setStyleSheet(Styles.TITLE_LABEL)
        self.language_combo.setStyleSheet(Styles.LANGUAGE_COMBO)
        
        logging.debug("TitleBar initialized.")