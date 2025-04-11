# ui/kpi_panel.py
from PyQt5 import QtWidgets, QtGui, QtCore
import logging
from typing import List, Dict, Any
from ui.styles import Styles

class KpiPanel(QtWidgets.QWidget):
    def __init__(self, kpis: List[str], tr_func, group: str):
        super().__init__()
        self.kpis = kpis
        self.tr = tr_func
        self.group = group
        self.setup_ui()
        logging.debug(f"KpiPanel initialized for group '{group}' with KPIs: {kpis}")

    def setup_ui(self):
        raise NotImplementedError("Subclasses must implement setup_ui()")

    def update_values(self, results: Dict[str, Any]):
        raise NotImplementedError("Subclasses must implement update_values()")

    def retranslate_ui(self):
        raise NotImplementedError("Subclasses must implement retranslate_ui()")

class TableKpiPanel(KpiPanel):
    def __init__(self, kpis: List[str], tr_func, group: str):
        super().__init__(kpis, tr_func, group)

    def setup_ui(self):
        self.table = QtWidgets.QTableWidget(len(self.kpis), 2)
        self.table.setHorizontalHeaderLabels([self.tr("KPI"), self.tr("Value")])
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        for i, kpi in enumerate(self.kpis):
            # Convert KPI key to a human-readable format that matches translation keys
            label = kpi.replace("_", " ").title()
            kpi_item = QtWidgets.QTableWidgetItem(self.tr(label))
            kpi_item.setForeground(QtGui.QColor("white"))
            kpi_item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.table.setItem(i, 0, kpi_item)
            value_item = QtWidgets.QTableWidgetItem("N/A")
            value_item.setForeground(QtGui.QColor("white"))
            value_item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.table.setItem(i, 1, value_item)
            logging.debug(f"Setup KPI {kpi} as '{self.tr(label)}'")
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.table)
        layout.setContentsMargins(0, 0, 0, 0)
        self.table.setStyleSheet(Styles.TABLE_PANEL)

    def update_values(self, results: Dict[str, Any]):
        for i, kpi in enumerate(self.kpis):
            value = results.get(kpi, "N/A")
            if isinstance(value, (int, float)):
                value = f"{value:.2f}"
            item = self.table.item(i, 1)
            if item is None:
                item = QtWidgets.QTableWidgetItem("N/A")
                item.setForeground(QtGui.QColor("white"))
                item.setFlags(QtCore.Qt.ItemIsEnabled)
                self.table.setItem(i, 1, item)
            item.setText(str(value))
            logging.debug(f"Updated {self.group} KPI {kpi}: {value}")

    def retranslate_ui(self):
        self.table.setHorizontalHeaderLabels([self.tr("KPI"), self.tr("Value")])
        for i, kpi in enumerate(self.kpis):
            label = kpi.replace("_", " ").title()
            translated_label = self.tr(label)
            item = self.table.item(i, 0)
            if item:
                item.setText(translated_label)
                logging.debug(f"Retranslated {kpi} to '{translated_label}'")
            else:
                logging.warning(f"Item at row {i} not found during retranslation for {kpi}")

class StateKpiPanel(KpiPanel):
    def __init__(self, kpis: List[str], tr_func, group: str):
        super().__init__(kpis, tr_func, group)

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        self.table = QtWidgets.QWidget()
        table_layout = QtWidgets.QGridLayout(self.table)
        table_layout.setColumnStretch(0, 1)
        table_layout.setColumnMinimumWidth(1, 120)
        self.state_labels = {}
        for i, kpi in enumerate(self.kpis):
            # Use title-case for the KPI name to match the translation dictionary
            translated_name = self.tr(kpi.replace("_", " ").title())
            name_label = QtWidgets.QLabel(translated_name)
            name_label.setStyleSheet(Styles.STATE_NAME_LABEL)
            table_layout.addWidget(name_label, i, 0, alignment=QtCore.Qt.AlignLeft)
            state_label = QtWidgets.QLabel(self.tr("None"))
            state_label.setFixedWidth(120)
            state_label.setStyleSheet(Styles.STATE_VALUE_DEFAULT)
            table_layout.addWidget(state_label, i, 1, alignment=QtCore.Qt.AlignRight)
            self.state_labels[kpi] = state_label
            logging.debug(f"Setup state KPI {kpi} as '{translated_name}'")
        self.table.setStyleSheet(Styles.STATE_PANEL)
        layout.addWidget(self.table)
        layout.addStretch()

    def update_values(self, results: Dict[str, Any]):
        for kpi in self.kpis:
            value = results.get(kpi, "N/A")
            state = "None" if value == "N/A" else str(value)
            label = self.state_labels[kpi]
            label.setText(self.tr(state))
            if state == "Pending":
                label.setStyleSheet(Styles.STATE_VALUE_PENDING)
            elif state.startswith("Detected"):
                label.setStyleSheet(Styles.STATE_VALUE_DETECTED)
            else:
                label.setStyleSheet(Styles.STATE_VALUE_DEFAULT)

    def retranslate_ui(self):
        for i, kpi in enumerate(self.kpis):
            translated_name = self.tr(kpi.replace("_", " ").title())
            name_label = self.table.layout().itemAtPosition(i, 0).widget()
            name_label.setText(translated_name)
            state_label = self.state_labels[kpi]
            current_state = state_label.text()
            translated_state = self.tr(current_state)
            state_label.setText(translated_state)
            logging.debug(f"Retranslated state KPI {kpi} to '{translated_name}', state to '{translated_state}'")
