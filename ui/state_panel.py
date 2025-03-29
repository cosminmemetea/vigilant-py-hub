from PyQt5 import QtWidgets, QtGui, QtCore
import logging

class StatePanel(QtWidgets.QWidget):
    def __init__(self, kpis, tr_func):
        super().__init__()
        self.tr = tr_func
        self.kpis = kpis
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        # Table-like widget for state KPIs
        self.table = QtWidgets.QWidget()
        table_layout = QtWidgets.QGridLayout(self.table)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(8)
        table_layout.setColumnStretch(0, 1)  # KPI name column stretches
        table_layout.setColumnMinimumWidth(1, 120)  # State column fixed at 120px
        
        self.state_labels = {}
        for i, kpi in enumerate(kpis):
            # KPI Name (Left-aligned)
            name_label = QtWidgets.QLabel(self.tr(kpi.capitalize().replace("_", " ")))
            name_label.setStyleSheet("""
                font: bold 14px 'Arial';
                color: #ECF0F1;
                padding: 5px;
                background: transparent;
            """)
            table_layout.addWidget(name_label, i, 0, alignment=QtCore.Qt.AlignLeft)
            
            # State (Right-aligned, fixed width)
            state_label = QtWidgets.QLabel(self.tr("None"))
            state_label.setFixedWidth(120)  # Fixed width to prevent resizing
            state_label.setStyleSheet("""
                font: 12px 'Arial';
                color: #2ECC71;
                background: rgba(46, 204, 113, 0.2);
                padding: 5px;
                border-radius: 4px;
                text-align: right;
            """)
            table_layout.addWidget(state_label, i, 1, alignment=QtCore.Qt.AlignRight)
            
            self.state_labels[kpi] = state_label
        
        self.table.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #34495E, stop:1 #2C3E50);
            border: 1px solid #444444;
            border-radius: 8px;
            padding: 5px;
        """)
        layout.addWidget(self.table)
        layout.addStretch()
        
        self.setStyleSheet("background: transparent;")
        logging.debug(f"StatePanel initialized with KPIs: {kpis}")

    def update_states(self, results):
        for kpi in self.kpis:
            value = results.get(kpi, "N/A")
            state = "None"
            if isinstance(value, str):
                state = value if value != "N/A" else "None"
            elif isinstance(value, dict):
                if kpi == "sleep":
                    if "microsleep" in self.kpis and "microsleep" == kpi:
                        state = value.get("microsleep", "None")
                    elif "sleep" in self.kpis and "sleep" == kpi:
                        state = value.get("sleep", "None")
                    else:
                        state = "None"
                else:
                    state = value.get("distraction", "None")
            
            label = self.state_labels[kpi]
            label.setText(self.tr(state))
            if state == "Pending":
                label.setStyleSheet("""
                    font: 12px 'Arial';
                    color: #F1C40F;
                    background: rgba(241, 196, 15, 0.2);
                    padding: 5px;
                    border-radius: 4px;
                    text-align: right;
                """)
            elif state.startswith("Detected"):
                label.setStyleSheet("""
                    font: 12px 'Arial';
                    color: #E74C3C;
                    background: rgba(231, 76, 60, 0.2);
                    padding: 5px;
                    border-radius: 4px;
                    text-align: right;
                """)
            else:
                label.setStyleSheet("""
                    font: 12px 'Arial';
                    color: #2ECC71;
                    background: rgba(46, 204, 113, 0.2);
                    padding: 5px;
                    border-radius: 4px;
                    text-align: right;
                """)

    def retranslate_ui(self):
        for i, kpi in enumerate(self.kpis):
            name_label = self.table.layout().itemAtPosition(i, 0).widget()
            state_label = self.state_labels[kpi]
            name_label.setText(self.tr(kpi.capitalize().replace("_", " ")))
            current_state = state_label.text()
            state_label.setText(self.tr(current_state))