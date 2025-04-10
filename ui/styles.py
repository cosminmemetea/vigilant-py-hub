class Styles:
    # Main Window
    MAIN_WINDOW = """
        QMainWindow {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #333333, stop:1 #1F1F1F);
        }
    """
    
    # Title Bar
    TITLE_BAR = """
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2E2E2E, stop:1 #1A1A1A);
        border-bottom: 1px solid #444444;
    """
    
    TITLE_LABEL = """
        font: bold 18px 'Arial';
        color: #3498DB;
        padding: 5px;
    """
    
    LANGUAGE_COMBO = """
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
    """
    
    # KPI Panels
    TABLE_PANEL = """
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
    """
    
    STATE_PANEL = """
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #34495E, stop:1 #2C3E50);
        border: 1px solid #444444;
        border-radius: 8px;
        padding: 5px;
    """
    
    STATE_NAME_LABEL = """
        font: bold 14px 'Arial';
        color: #ECF0F1;
        padding: 5px;
        background: transparent;
    """
    
    STATE_VALUE_DEFAULT = """
        font: 12px 'Arial';
        color: #2ECC71;
        background: rgba(46, 204, 113, 0.2);
        padding: 5px;
        border-radius: 4px;
        text-align: right;
    """
    
    STATE_VALUE_PENDING = """
        font: 12px 'Arial';
        color: #F1C40F;
        background: rgba(241, 196, 15, 0.2);
        padding: 5px;
        border-radius: 4px;
        text-align: right;
    """
    
    STATE_VALUE_DETECTED = """
        font: 12px 'Arial';
        color: #E74C3C;
        background: rgba(231, 76, 60, 0.2);
        padding: 5px;
        border-radius: 4px;
        text-align: right;
    """
    
    # Video Panel
    VIDEO_PANEL = """
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2E2E2E, stop:1 #1A1A1A);
        border-radius: 10px;
    """
    
    VIDEO_LABEL_DEFAULT = """
        background-color: #1C2526;
        border: 2px solid #3498DB;
        border-radius: 12px;
        font: bold 16px "Arial";
        color: #ECF0F1;
    """
    
    VIDEO_LABEL_ALERT = """
        background-color: #1C2526;
        border: 2px solid #E74C3C;
        border-radius: 12px;
        font: bold 16px "Arial";
        color: #ECF0F1;
    """
    
    # Button (corrected with f-string)
    @staticmethod
    def BUTTON(color="#3498DB", hover_color="#2980B9"):
        return f"""
            QPushButton {{
                background-color: {color};
                border-radius: 6px;
                padding: 8px 16px;
                font: bold 12px "Arial";
                color: white;
                border: 1px solid #444444;
            }}
            QPushButton:disabled {{
                background-color: #7F8C8D;
            }}
            QPushButton:hover:enabled {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {hover_color};
                border: 1px solid #555555;
            }}
        """