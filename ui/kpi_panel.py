# ui/kpi_panel.py
# Defines KPI panel classes for displaying Key Performance Indicators (KPIs) in a PyQt5 GUI.

from PyQt5 import QtWidgets, QtGui, QtCore  # PyQt5 modules for creating GUI components.
import logging  # Facilitates logging for debugging and monitoring UI updates.
from typing import List, Dict, Any  # Type hints for lists, dictionaries, and flexible data.
from ui.styles import Styles  # Custom styles for consistent UI appearance.

class KpiPanel(QtWidgets.QWidget):
    def __init__(self, kpis: List[str], tr_func, group: str):
        """Initialize the base KpiPanel for displaying KPIs.

        Args:
            kpis: List of KPI names to display.
            tr_func: Translation function for internationalization.
            group: Group name for categorizing KPIs (e.g., 'numeric', 'state').
        """
        super().__init__()  # Initialize base QWidget class.
        self.kpis = kpis  # Store list of KPI names.
        self.tr = tr_func  # Store translation function for dynamic text updates.
        self.group = group  # Store group name for categorization.
        self.setup_ui()  # Set up the UI (implemented by subclasses).
        logging.debug(f"KpiPanel initialized for group '{group}' with KPIs: {kpis}")

    def setup_ui(self):
        """Set up the panel's UI layout and widgets.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement setup_ui()")

    def update_values(self, results: Dict[str, Any]):
        """Update KPI values displayed in the panel.

        Args:
            results: Dictionary mapping KPI names to their values.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement update_values()")

    def retranslate_ui(self):
        """Update UI text with translated strings.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement retranslate_ui()")

class TableKpiPanel(KpiPanel):
    def __init__(self, kpis: List[str], tr_func, group: str):
        """Initialize a TableKpiPanel for displaying numeric KPIs in a table.

        Args:
            kpis: List of KPI names to display.
            tr_func: Translation function for internationalization.
            group: Group name for categorizing KPIs.
        """
        super().__init__(kpis, tr_func, group)

    def setup_ui(self):
        """Set up a table-based UI for displaying KPI names and values."""
        # Create a table with rows for each KPI and two columns (name, value).
        self.table = QtWidgets.QTableWidget(len(self.kpis), 2)
        self.table.setHorizontalHeaderLabels([self.tr("KPI"), self.tr("Value")])  # Set column headers.
        self.table.verticalHeader().setVisible(False)  # Hide row numbers.
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)  # Stretch columns to fit.
        for i, kpi in enumerate(self.kpis):
            # Convert KPI name to human-readable format (e.g., 'left_eye_openness' to 'Left Eye Openness').
            label = kpi.replace("_", " ").title()
            # Create non-editable item for KPI name.
            kpi_item = QtWidgets.QTableWidgetItem(self.tr(label))
            kpi_item.setForeground(QtGui.QColor("white"))  # Set text color.
            kpi_item.setFlags(QtCore.Qt.ItemIsEnabled)  # Disable editing.
            self.table.setItem(i, 0, kpi_item)
            # Create non-editable item for KPI value, initialized as 'N/A'.
            value_item = QtWidgets.QTableWidgetItem("N/A")
            value_item.setForeground(QtGui.QColor("white"))
            value_item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.table.setItem(i, 1, value_item)
            logging.debug(f"Setup KPI {kpi} as '{self.tr(label)}'")
        # Add table to a vertical layout.
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.table)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins for tight fit.
        self.table.setStyleSheet(Styles.TABLE_PANEL)  # Apply custom table styling.

    def update_values(self, results: Dict[str, Any]):
        """Update KPI values in the table based on results.

        Args:
            results: Dictionary mapping KPI names to their values.
        """
        for i, kpi in enumerate(self.kpis):
            value = results.get(kpi, "N/A")  # Get value or default to 'N/A'.
            if isinstance(value, (int, float)):
                value = f"{value:.2f}"  # Format numeric values to two decimal places.
            item = self.table.item(i, 1)  # Get value cell.
            if item is None:
                # Create new item if none exists (defensive programming).
                item = QtWidgets.QTableWidgetItem("N/A")
                item.setForeground(QtGui.QColor("white"))
                item.setFlags(QtCore.Qt.ItemIsEnabled)
                self.table.setItem(i, 1, item)
            item.setText(str(value))  # Update cell with new value.
            logging.debug(f"Updated {self.group} KPI {kpi}: {value}")

    def retranslate_ui(self):
        """Update table text with translated strings."""
        self.table.setHorizontalHeaderLabels([self.tr("KPI"), self.tr("Value")])  # Update headers.
        for i, kpi in enumerate(self.kpis):
            label = kpi.replace("_", " ").title()  # Convert to human-readable format.
            translated_label = self.tr(label)  # Get translated label.
            item = self.table.item(i, 0)  # Get KPI name cell.
            if item:
                item.setText(translated_label)  # Update with translated text.
                logging.debug(f"Retranslated {kpi} to '{translated_label}'")
            else:
                logging.warning(f"Item at row {i} not found during retranslation for {kpi}")

class StateKpiPanel(KpiPanel):
    def __init__(self, kpis: List[str], tr_func, group: str):
        """Initialize a StateKpiPanel for displaying state-based KPIs.

        Args:
            kpis: List of KPI names to display.
            tr_func: Translation function for internationalization.
            group: Group name for categorizing KPIs.
        """
        super().__init__(kpis, tr_func, group)

    def setup_ui(self):
        """Set up a grid-based UI for displaying state KPI names and values."""
        layout = QtWidgets.QVBoxLayout(self)  # Create main vertical layout.
        self.table = QtWidgets.QWidget()  # Create widget to hold grid layout.
        table_layout = QtWidgets.QGridLayout(self.table)  # Create grid for name-value pairs.
        table_layout.setColumnStretch(0, 1)  # Stretch name column to fill space.
        table_layout.setColumnMinimumWidth(1, 120)  # Set fixed width for value column.
        self.state_labels = {}  # Store value labels for each KPI.
        for i, kpi in enumerate(self.kpis):
            # Convert KPI name to human-readable and translated format.
            translated_name = self.tr(kpi.replace("_", " ").title())
            # Create label for KPI name.
            name_label = QtWidgets.QLabel(translated_name)
            name_label.setStyleSheet(Styles.STATE_NAME_LABEL)  # Apply name styling.
            table_layout.addWidget(name_label, i, 0, alignment=QtCore.Qt.AlignLeft)
            # Create label for KPI state, initialized as 'None'.
            state_label = QtWidgets.QLabel(self.tr("None"))
            state_label.setFixedWidth(120)  # Fix width for consistency.
            state_label.setStyleSheet(Styles.STATE_VALUE_DEFAULT)  # Apply default state styling.
            table_layout.addWidget(state_label, i, 1, alignment=QtCore.Qt.AlignRight)
            self.state_labels[kpi] = state_label  # Store state label for updates.
            logging.debug(f"Setup state KPI {kpi} as '{translated_name}'")
        self.table.setStyleSheet(Styles.STATE_PANEL)  # Apply panel styling.
        layout.addWidget(self.table)  # Add grid widget to layout.
        layout.addStretch()  # Add stretch to push content upward.
        # layout.setContentsMargins(0, 0, 0, 0)  # Uncomment if margins need removal.

    def update_values(self, results: Dict[str, Any]):
        """Update state KPI values and styles based on results.

        Args:
            results: Dictionary mapping KPI names to their state values.
        """
        for kpi in self.kpis:
            value = results.get(kpi, "N/A")  # Get state or default to 'N/A'.
            state = "None" if value == "N/A" else str(value)  # Convert to string state.
            label = self.state_labels[kpi]  # Get state label.
            label.setText(self.tr(state))  # Update with translated state.
            # Apply styling based on state value.
            if state == "Pending":
                label.setStyleSheet(Styles.STATE_VALUE_PENDING)
            elif state.startswith("Detected"):
                label.setStyleSheet(Styles.STATE_VALUE_DETECTED)
            else:
                label.setStyleSheet(Styles.STATE_VALUE_DEFAULT)
            logging.debug(f"Updated {self.group} KPI {kpi}: {state}")

    def retranslate_ui(self):
        """Update state panel text with translated strings."""
        for i, kpi in enumerate(self.kpis):
            translated_name = self.tr(kpi.replace("_", " ").title())  # Get translated KPI name.
            name_label = self.table.layout().itemAtPosition(i, 0).widget()  # Get name label.
            name_label.setText(translated_name)  # Update name.
            state_label = self.state_labels[kpi]  # Get state label.
            current_state = state_label.text()  # Get current state text.
            translated_state = self.tr(current_state)  # Translate state.
            state_label.setText(translated_state)  # Update state.
            logging.debug(f"Retranslated state KPI {kpi} to '{translated_name}', state to '{translated_state}'")