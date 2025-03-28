# ui/kpi_table.py
from PyQt5 import QtWidgets, QtGui, QtCore
import logging

class KPITable(QtWidgets.QTableWidget):
    def __init__(self, rows, kpis, tr_func):
        super().__init__(rows, 2)
        self.tr = tr_func
        self.kpis = kpis
        self.setup_ui()
        logging.debug(f"KPITable initialized with {rows} rows and KPIs: {kpis}")
    
    def setup_ui(self):
        # Set up the KPI table
        self.setHorizontalHeaderLabels([self.tr("KPI"), self.tr("Value")])
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        for i, kpi in enumerate(self.kpis):
            kpi_item = QtWidgets.QTableWidgetItem(self.tr(kpi))
            kpi_item.setForeground(QtGui.QColor("white"))
            kpi_item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.setItem(i, 0, kpi_item)
            value_item = QtWidgets.QTableWidgetItem("N/A")
            value_item.setForeground(QtGui.QColor("white"))
            value_item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.setItem(i, 1, value_item)
        self.setStyleSheet("""
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
    
    def update_values(self, results):
        # Update KPI values in the table
        for i, kpi in enumerate(self.kpis):
            value = results.get(kpi.lower().replace(" ", "_"), "N/A")
            if isinstance(value, (int, float)):
                value = f"{value:.2f}"
            elif value is None:
                value = "N/A"
            self.item(i, 1).setText(str(value))